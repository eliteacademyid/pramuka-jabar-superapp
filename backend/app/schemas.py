from datetime import date, datetime
from typing import Optional
from uuid import UUID

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


# Membership Schemas
class MemberCardOut(BaseModel):
    """Response schema for member digital card - includes all card information"""
    id: int
    nama_lengkap: str
    nomor_anggota: Optional[str] = None
    golongan: Optional[str] = None
    kwartir: Optional[str] = None
    membership_status: str
    valid_until: Optional[date] = None
    foto_url: Optional[str] = None
    verification_token: UUID

    model_config = {"from_attributes": True}


class VerificationOut(BaseModel):
    """Response schema for public verification - limited information only"""
    nama_lengkap: str
    nomor_anggota: Optional[str] = None
    golongan: Optional[str] = None
    kwartir: Optional[str] = None
    membership_status: str
    
    model_config = {"from_attributes": True}


class QRCodeOut(BaseModel):
    """Response schema for QR code data"""
    qr_code_url: str
    verification_url: str
