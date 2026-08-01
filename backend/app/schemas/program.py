from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ProgramBase(BaseModel):
    nama: str
    deskripsi: Optional[str] = None
    tahun: int
    status: str = "active"


class ProgramCreate(ProgramBase):
    organisasi_id: int


class ProgramUpdate(BaseModel):
    nama: Optional[str] = None
    deskripsi: Optional[str] = None
    tahun: Optional[int] = None
    status: Optional[str] = None


class ProgramResponse(ProgramBase):
    id: int
    creator_id: int
    organisasi_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProgramDetailResponse(ProgramResponse):
    pass
