from bcrypt import checkpw, hashpw, gensalt

# rounds=10 ~60ms (default 12 ~250ms). Masih aman untuk production,
# dan menjaga response time login tetap di bawah 200ms.
_BCRYPT_ROUNDS = 10


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return hashpw(password.encode("utf-8"), gensalt(rounds=_BCRYPT_ROUNDS)).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hashed password"""
    return checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
