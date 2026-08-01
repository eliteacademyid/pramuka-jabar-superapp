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


class TrainingBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    passing_grade: int = 70
    status: str = "Draft"


class TrainingCreate(TrainingBase):
    pass


class TrainingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    passing_grade: Optional[int] = None
    status: Optional[str] = None


class TrainingOut(TrainingBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TrainingMaterialBase(BaseModel):
    title: str
    content: Optional[str] = None
    media_url: Optional[str] = None
    order: int = 1


class TrainingMaterialCreate(TrainingMaterialBase):
    training_id: int


class TrainingMaterialUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    media_url: Optional[str] = None
    order: Optional[int] = None


class TrainingMaterialOut(TrainingMaterialBase):
    id: int
    training_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


