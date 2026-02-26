import json
from datetime import date
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def fetch_gmail_emails(gmail_token: str, query: str = None) -> list[dict[str, Any]]:
    """
    Fetch today's emails from Gmail that may contain shortlist/placement info.

    Args:
        gmail_token: JSON-encoded Google OAuth credentials.
        query: Optional Gmail search query. Defaults to shortlist-related terms.

    Returns:
        List of email metadata dicts with id, subject, sender, snippet, date,
        and has_attachment flag.
    """
    token_data = json.loads(gmail_token)
    credentials = Credentials(
        token=token_data["token"],
        refresh_token=token_data.get("refresh_token"),
        token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=token_data.get("client_id"),
        client_secret=token_data.get("client_secret"),
        scopes=token_data.get("scopes", []),
    )

    service = build("gmail", "v1", credentials=credentials)

    # Default query: today's shortlist/placement emails only
    today = date.today().strftime("%Y/%m/%d")
    if not query:
        query = f"after:{today} subject:(shortlist OR shortlisted OR placement OR selected OR exam date)"
    else:
        # Always restrict to today even with custom queries
        query = f"after:{today} {query}"

    results = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=10)
        .execute()
    )

    messages = results.get("messages", [])
    if not messages:
        return []

    emails = []
    for msg_meta in messages:
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=msg_meta["id"], format="metadata")
            .execute()
        )

        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        parts = msg.get("payload", {}).get("parts", [])
        has_attachment = any(
            part.get("filename") and part["filename"] != ""
            for part in parts
        ) if parts else False

        emails.append(
            {
                "id": msg["id"],
                "subject": headers.get("Subject", ""),
                "sender": headers.get("From", ""),
                "date": headers.get("Date", ""),
                "snippet": msg.get("snippet", ""),
                "has_attachment": has_attachment,
            }
        )

    return emails
