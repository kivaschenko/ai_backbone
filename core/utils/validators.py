"""
Validation utilities for data integrity.
"""

from typing import Dict, Any, List
from datetime import datetime
import re


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid email format
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.

    Args:
        phone: Phone number to validate

    Returns:
        True if valid phone format
    """
    # Remove common separators
    cleaned = re.sub(r"[\s\-\(\)\.]", "", phone)
    # Check if it's 10-15 digits
    return bool(re.match(r"^\+?\d{10,15}$", cleaned))


def validate_required_fields(
    data: Dict[str, Any], required_fields: List[str]
) -> tuple[bool, List[str]]:
    """
    Validate that required fields are present in data.

    Args:
        data: Data dictionary to validate
        required_fields: List of required field names

    Returns:
        Tuple of (is_valid, missing_fields)
    """
    missing = [
        field for field in required_fields if field not in data or data[field] is None
    ]
    return len(missing) == 0, missing


def validate_date_format(date_string: str, format_string: str = "%Y-%m-%d") -> bool:
    """
    Validate date string format.

    Args:
        date_string: Date string to validate
        format_string: Expected date format

    Returns:
        True if valid date format
    """
    try:
        datetime.strptime(date_string, format_string)
        return True
    except (ValueError, TypeError):
        return False


def validate_numeric_range(
    value: float, min_value: float = None, max_value: float = None
) -> bool:
    """
    Validate that a numeric value is within a specified range.

    Args:
        value: Value to validate
        min_value: Minimum acceptable value (inclusive)
        max_value: Maximum acceptable value (inclusive)

    Returns:
        True if value is within range
    """
    if min_value is not None and value < min_value:
        return False
    if max_value is not None and value > max_value:
        return False
    return True


def sanitize_string(text: str, max_length: int = None) -> str:
    """
    Sanitize string by removing potentially dangerous characters.

    Args:
        text: Text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove null bytes and control characters
    sanitized = text.replace("\x00", "").strip()

    # Truncate if needed
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized
