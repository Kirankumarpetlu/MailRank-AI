import json
import os
from typing import Any

from groq import Groq
from sqlalchemy.orm import Session

from config import settings
from mcp_server import MCPServer
from models import User
from tools.gmail import fetch_gmail_emails
from tools.attachment import download_attachment
from tools.excel import parse_excel
from tools.shortlist import check_shortlist
from tools.result import save_result


class ShortlistAgent:
    """
    AI-powered agent using Groq LLM that orchestrates MCP tools to check
    if a user has been shortlisted via their Gmail emails.

    Flow:
    1. fetch_gmail_emails — search for placement/shortlist emails
    2. identify shortlist emails with attachments
    3. download_attachment — download Excel attachment
    4. parse_excel — parse the spreadsheet
    5. check_shortlist — match user's registration ID / email
    6. Use Groq LLM to analyze email content for intelligent matching
    7. save_result — persist the result to DB
    8. Return structured JSON: {status, company, exam_date}
    """

    GROQ_MODEL = "llama-3.3-70b-versatile"

    def __init__(self, mcp: MCPServer, db: Session, user: User):
        self.mcp = mcp
        self.db = db
        self.user = user
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
        self._register_tools()

    def _register_tools(self):
        """Register all MCP tools with the server."""
        self.mcp.register_tool(
            "fetch_gmail_emails",
            fetch_gmail_emails,
            "Search Gmail for shortlist/placement emails",
        )
        self.mcp.register_tool(
            "download_attachment",
            download_attachment,
            "Download an attachment from a Gmail message",
        )
        self.mcp.register_tool(
            "parse_excel",
            parse_excel,
            "Parse an Excel .xlsx file into row dicts",
        )
        self.mcp.register_tool(
            "check_shortlist",
            check_shortlist,
            "Check if user is shortlisted in parsed data",
        )
        self.mcp.register_tool(
            "save_result",
            self._save_result_wrapper,
            "Save the shortlist result to the database",
        )

    def _save_result_wrapper(self, **kwargs) -> dict:
        """Wrapper that injects db and user_id into save_result."""
        return save_result(
            db=self.db,
            user_id=self.user.id,
            **kwargs,
        )

    def _ask_groq(self, prompt: str) -> str:
        """Send a prompt to Groq LLM and return the response text."""
        try:
            chat = self.groq_client.chat.completions.create(
                model=self.GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an AI assistant that analyzes emails to determine "
                            "if a student/candidate has been shortlisted for a job placement. "
                            "Extract company name and exam date if found. "
                            "Respond ONLY in valid JSON with keys: "
                            "shortlisted (bool), company (string or null), exam_date (string or null), "
                            "confidence (float 0-1), reasoning (string)."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=512,
            )
            return chat.choices[0].message.content
        except Exception as e:
            print(f"Groq API error: {e}")
            return json.dumps({
                "shortlisted": False,
                "company": None,
                "exam_date": None,
                "confidence": 0,
                "reasoning": f"LLM error: {str(e)}",
            })

    def _analyze_email_with_llm(self, email_msg: dict) -> dict:
        """Use Groq LLM to intelligently analyze an email for shortlist info."""
        prompt = (
            f"Analyze this email and determine if the recipient has been shortlisted "
            f"for a job/placement:\n\n"
            f"Subject: {email_msg.get('subject', 'N/A')}\n"
            f"From: {email_msg.get('sender', 'N/A')}\n"
            f"Date: {email_msg.get('date', 'N/A')}\n"
            f"Snippet: {email_msg.get('snippet', 'N/A')}\n\n"
            f"Has attachment: {email_msg.get('has_attachment', False)}\n\n"
            f"Is this a shortlist/selection notification? Extract company name and exam date if present."
        )

        response_text = self._ask_groq(prompt)

        try:
            # Strip markdown code fences if present
            cleaned = response_text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]  # remove first line
                cleaned = cleaned.rsplit("```", 1)[0]  # remove last fence
            return json.loads(cleaned)
        except (json.JSONDecodeError, IndexError):
            return {
                "shortlisted": False,
                "company": None,
                "exam_date": None,
                "confidence": 0,
                "reasoning": "Failed to parse LLM response",
            }

    async def run(self) -> dict[str, Any]:
        """
        Execute the full shortlist-checking pipeline via MCP tools + Groq LLM.

        Returns:
            Structured result: {status, company, exam_date}
        """
        try:
            # ── Step 1: Fetch Gmail emails ───────────────────────────
            email_result = await self.mcp.execute_tool(
                "fetch_gmail_emails",
                {"gmail_token": self.user.gmail_token},
            )

            if not email_result["success"]:
                return await self._finalize("error", error=email_result["error"])

            emails = email_result["result"]
            if not emails:
                return await self._finalize("not_selected")

            # ── Step 2: Process emails with attachments ──────────────
            for email_msg in emails:
                if not email_msg.get("has_attachment"):
                    continue

                # Step 3: Download attachment
                att_result = await self.mcp.execute_tool(
                    "download_attachment",
                    {
                        "gmail_token": self.user.gmail_token,
                        "message_id": email_msg["id"],
                    },
                )

                if not att_result["success"] or not att_result["result"]:
                    continue

                file_path = att_result["result"]

                # Step 4: Parse Excel
                parse_result = await self.mcp.execute_tool(
                    "parse_excel",
                    {"file_path": file_path},
                )

                # Clean up temp file
                try:
                    os.unlink(file_path)
                except OSError:
                    pass

                if not parse_result["success"] or not parse_result["result"]:
                    continue

                parsed_data = parse_result["result"]

                # Step 5: Check shortlist (rule-based)
                shortlist_result = await self.mcp.execute_tool(
                    "check_shortlist",
                    {
                        "parsed_data": parsed_data,
                        "registration_id": self.user.registration_id,
                        "email": self.user.email,
                    },
                )

                if not shortlist_result["success"]:
                    continue

                result = shortlist_result["result"]
                if result.get("shortlisted"):
                    return await self._finalize(
                        "selected",
                        company=result.get("company"),
                        exam_date=result.get("exam_date"),
                    )

            # ── Step 6: LLM-powered email analysis ─────────────────
            # Use Groq LLM to intelligently analyze email content
            for email_msg in emails:
                llm_result = self._analyze_email_with_llm(email_msg)

                if (
                    llm_result.get("shortlisted")
                    and llm_result.get("confidence", 0) >= 0.7
                ):
                    return await self._finalize(
                        "selected",
                        company=llm_result.get("company") or "Unknown Company",
                        exam_date=llm_result.get("exam_date") or "TBD",
                    )

            # No shortlist found
            return await self._finalize("not_selected")

        except Exception as e:
            print(f"Agent error: {e}")
            return await self._finalize("error", error=str(e))

    async def _finalize(
        self,
        status: str,
        company: str = None,
        exam_date: str = None,
        error: str = None,
    ) -> dict[str, Any]:
        """Save result to DB and return structured response."""
        # Save to database
        await self.mcp.execute_tool(
            "save_result",
            {
                "status": status,
                "company": company,
                "exam_date": exam_date,
            },
        )

        result = {
            "status": status,
            "shortlisted": status == "selected",
            "company": company,
            "exam_date": exam_date,
        }
        if error:
            result["error"] = error

        return result
