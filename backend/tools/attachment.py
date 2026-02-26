import json
import os
import tempfile
from typing import Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64


def download_attachment(
    gmail_token: str, message_id: str, attachment_id: str = None, filename: str = None
) -> Optional[str]:
    """
    Download an attachment from a Gmail message.

    Args:
        gmail_token: JSON-encoded Google OAuth credentials.
        message_id: The Gmail message ID.
        attachment_id: Optional specific attachment ID. If not provided,
                       downloads the first attachment found.
        filename: Optional filename hint for the saved file.

    Returns:
        Path to the downloaded temporary file, or None if no attachment found.
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

    # Get full message to find attachments
    msg = (
        service.users()
        .messages()
        .get(userId="me", id=message_id, format="full")
        .execute()
    )

    parts = msg.get("payload", {}).get("parts", [])
    target_part = None

    for part in parts:
        part_filename = part.get("filename", "")
        body = part.get("body", {})
        att_id = body.get("attachmentId")

        if not part_filename or not att_id:
            continue

        if attachment_id and att_id == attachment_id:
            target_part = part
            break
        elif not attachment_id:
            # Take the first attachment
            target_part = part
            break

    if not target_part:
        return None

    att_id = target_part["body"]["attachmentId"]
    att_filename = target_part.get("filename", filename or "attachment")

    attachment = (
        service.users()
        .messages()
        .attachments()
        .get(userId="me", messageId=message_id, id=att_id)
        .execute()
    )

    data = attachment.get("data", "")
    file_data = base64.urlsafe_b64decode(data)

    # Save to temp file
    ext = os.path.splitext(att_filename)[1] or ".xlsx"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext, prefix="shortlist_")
    tmp.write(file_data)
    tmp.close()

    return tmp.name
