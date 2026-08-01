from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class OrganisasiBase(BaseModel):
    nama: str
    alamat: Optional[str] = None
    telepon: Optional[str] = None
    email: Optional[EmailStr] = None


class OrganisasiCreate(OrganisasiBase):
    pass


class OrganisasiUpdate(BaseModel):
    nama: Optional[str] = None
    alamat: Optional[str] = None
    telepon: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class OrganisasiResponse(OrganisasiBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
