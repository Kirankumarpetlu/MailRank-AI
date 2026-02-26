from typing import Any, Optional


def check_shortlist(
    parsed_data: list[dict[str, Any]],
    registration_id: str = None,
    email: str = None,
) -> dict[str, Any]:
    """
    Check if a user is shortlisted based on parsed Excel data.

    Searches the parsed rows for a match by registration_id or email.

    Args:
        parsed_data: List of row dicts from parse_excel.
        registration_id: User's registration ID to search for.
        email: User's email to search for as fallback.

    Returns:
        Dict with shortlisted status, company, and exam_date.
    """
    if not parsed_data:
        return {"shortlisted": False, "company": None, "exam_date": None}

    for row in parsed_data:
        row_lower = {str(k).lower(): str(v).lower() if v else "" for k, v in row.items()}

        # Try matching by registration ID
        matched = False
        if registration_id:
            reg_id_lower = registration_id.lower()
            for key, val in row_lower.items():
                if "reg" in key or "id" in key or "roll" in key:
                    if reg_id_lower in val:
                        matched = True
                        break

        # Fallback: match by email
        if not matched and email:
            email_lower = email.lower()
            for val in row_lower.values():
                if email_lower in val:
                    matched = True
                    break

        if matched:
            # Extract company name
            company = _extract_field(row, ["company", "organization", "org", "firm"])
            # Extract exam date
            exam_date = _extract_field(row, ["exam date", "date", "exam_date", "test date"])

            return {
                "shortlisted": True,
                "company": company or "Unknown Company",
                "exam_date": str(exam_date) if exam_date else "TBD",
            }

    return {"shortlisted": False, "company": None, "exam_date": None}


def _extract_field(row: dict, possible_keys: list[str]) -> Optional[str]:
    """Extract a field value by trying multiple possible column names."""
    for key in row:
        key_lower = str(key).lower()
        for candidate in possible_keys:
            if candidate in key_lower:
                val = row[key]
                return str(val) if val else None
    return None
