"""
Input validators
"""
import re


def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate username

    Args:
        username: Username to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"

    if len(username) < 3:
        return False, "Username must be at least 3 characters long"

    if len(username) > 20:
        return False, "Username must be at most 20 characters long"

    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"

    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"

    if len(password) < 6:
        return False, "Password must be at least 6 characters long"

    if len(password) > 100:
        return False, "Password is too long"

    return True, ""


def validate_email(email: str) -> tuple[bool, str]:
    """
    Validate email address

    Args:
        email: Email to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return True, ""  # Email is optional

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Invalid email format"

    return True, ""


def validate_move(position: int) -> tuple[bool, str]:
    """
    Validate move position

    Args:
        position: Position to validate (0-8)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(position, int):
        return False, "Position must be an integer"

    if position < 0 or position > 8:
        return False, "Position must be between 0 and 8"

    return True, ""
