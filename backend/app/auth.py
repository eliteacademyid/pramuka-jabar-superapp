from app.utils.password import hash_password as hash_password_impl
from app.utils.password import verify_password as verify_password_impl
from app.utils.security import (
    create_access_token as create_access_token_impl,
    create_refresh_token as create_refresh_token_impl,
    verify_token as verify_token_impl,
)


def hash_password(password: str) -> str:
    return hash_password_impl(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return verify_password_impl(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    return create_access_token_impl(data)


def create_refresh_token(data: dict) -> str:
    return create_refresh_token_impl(data)


def verify_token(token: str) -> dict | None:
    return verify_token_impl(token)


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
]
