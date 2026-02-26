import json
import os

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models import User
from jwt_utils import create_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Path to the credentials.json file
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "credentials.json")


def _create_flow() -> Flow:
    """Create a Google OAuth flow from credentials.json."""
    # Load credentials.json and adapt for web flow
    with open(CREDENTIALS_FILE, "r") as f:
        creds_data = json.load(f)

    # Handle both "installed" and "web" credential types
    if "installed" in creds_data:
        client_config = {
            "web": {
                "client_id": creds_data["installed"]["client_id"],
                "client_secret": creds_data["installed"]["client_secret"],
                "auth_uri": creds_data["installed"]["auth_uri"],
                "token_uri": creds_data["installed"]["token_uri"],
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
            }
        }
    elif "web" in creds_data:
        client_config = creds_data
    else:
        raise ValueError("Invalid credentials.json format")

    flow = Flow.from_client_config(
        client_config,
        scopes=settings.SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )
    return flow


@router.get("/login")
async def login():
    """Redirect user to Google consent screen."""
    flow = _create_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback."""
    code = request.query_params.get("code")
    if not code:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/?error=no_code")

    try:
        # Exchange authorization code for tokens
        flow = _create_flow()
        flow.fetch_token(code=code)
        credentials: Credentials = flow.credentials

        # Fetch user profile from Google
        service = build("oauth2", "v2", credentials=credentials)
        user_info = service.userinfo().get().execute()

        email = user_info.get("email", "")
        full_name = user_info.get("name", "")

        # Serialize Gmail token for storage
        token_data = json.dumps(
            {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": list(credentials.scopes) if credentials.scopes else [],
            }
        )

        # Upsert user
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.gmail_token = token_data
            user.full_name = full_name
        else:
            user = User(
                email=email,
                full_name=full_name,
                gmail_token=token_data,
            )
            db.add(user)

        db.commit()
        db.refresh(user)

        # Generate JWT
        jwt_token = create_token({"sub": email, "user_id": user.id})

        # Redirect to frontend with token
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/?token={jwt_token}"
        )

    except Exception as e:
        print(f"OAuth callback error: {e}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/?error=auth_failed"
        )
