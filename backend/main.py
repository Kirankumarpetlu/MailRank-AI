import os

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from config import settings
from database import get_db, init_db
from auth import router as auth_router
from jwt_utils import get_current_user
from models import User
from mcp_server import MCPServer
from agent import ShortlistAgent

app = FastAPI(
    title="Shortlist AI",
    description="Automatically detect placement shortlist emails from Gmail",
    version="1.0.0",
)

# CORS — allow frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:8080", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount auth routes
app.include_router(auth_router)


@app.on_event("startup")
def on_startup():
    """Initialize the database on server start."""
    init_db()


# ── Serve the frontend ──
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")


@app.get("/")
async def root():
    """Serve the frontend index.html."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"message": "Shortlist AI API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/check-shortlist")
async def check_shortlist_endpoint(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Check if the authenticated user has been shortlisted.

    Flow:
    1. Validate JWT → get current user
    2. Create MCPServer and register all tools
    3. Initialize ShortlistAgent with MCP server
    4. Run agent pipeline
    5. Return structured result JSON
    """
    # Create MCP server and agent
    mcp = MCPServer()
    agent = ShortlistAgent(mcp=mcp, db=db, user=user)

    # Run the agent pipeline
    result = await agent.run()

    return result
