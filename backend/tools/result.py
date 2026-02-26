import datetime

from sqlalchemy.orm import Session

from models import ShortlistResult


def save_result(
    db: Session,
    user_id: int,
    status: str,
    company: str = None,
    exam_date: str = None,
) -> dict:
    """
    Save a shortlist check result to the database.

    Args:
        db: SQLAlchemy database session.
        user_id: The user's ID.
        status: Result status — 'selected', 'not_selected', or 'error'.
        company: Company name (if shortlisted).
        exam_date: Exam date string (if shortlisted).

    Returns:
        Dict confirming the saved result.
    """
    result = ShortlistResult(
        user_id=user_id,
        company=company,
        exam_date=exam_date,
        status=status,
        checked_at=datetime.datetime.utcnow(),
    )
    db.add(result)
    db.commit()
    db.refresh(result)

    return {
        "id": result.id,
        "status": result.status,
        "company": result.company,
        "exam_date": result.exam_date,
        "checked_at": str(result.checked_at),
    }
