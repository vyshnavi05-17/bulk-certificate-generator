import re
from typing import Any, Dict, Optional, Tuple

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def validate_recipient_data(raw_data: Any) -> Tuple[bool, Optional[str], Optional[Dict[str, str]]]:
    """
    Validates individual recipient data in the worker.
    Returns:
        (is_valid: bool, error_message: Optional[str], cleaned_data: Optional[Dict[str, str]])
    """
    if not isinstance(raw_data, dict):
        # Could be a Pydantic model with model_dump or dict
        if hasattr(raw_data, "model_dump"):
            raw_data = raw_data.model_dump()
        elif hasattr(raw_data, "dict"):
            raw_data = raw_data.dict()
        else:
            return False, "Recipient record must be an object with name and email", None

    name = raw_data.get("name")
    email = raw_data.get("email")

    # Validate name
    if name is None or not isinstance(name, str) or not name.strip():
        return False, "Recipient name is required and cannot be blank", None

    cleaned_name = name.strip()

    # Validate email
    if email is None or not isinstance(email, str) or not email.strip():
        return False, "Recipient email is required and cannot be blank", None

    cleaned_email = email.strip()

    # Try email-validator library if available, otherwise regex fallback
    try:
        from email_validator import validate_email, EmailNotValidError
        try:
            valid_email_info = validate_email(cleaned_email, check_deliverability=False)
            cleaned_email = valid_email_info.normalized
        except EmailNotValidError as exc:
            return False, f"Invalid email format: {str(exc)}", None
    except ImportError:
        if not EMAIL_REGEX.match(cleaned_email):
            return False, "Invalid email address format", None

    return True, None, {"name": cleaned_name, "email": cleaned_email}
