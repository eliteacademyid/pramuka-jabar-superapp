from bcrypt import checkpw, hashpw, gensalt


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hashed password"""
    return checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
