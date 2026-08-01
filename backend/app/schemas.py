from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models import ROLES


class LoginRequest(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str
    nama_lengkap: str
    role: str = "staff"


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    nama_lengkap: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    username: str
    nama_lengkap: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str
