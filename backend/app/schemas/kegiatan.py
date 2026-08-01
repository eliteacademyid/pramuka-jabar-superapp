from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class KegiatanBase(BaseModel):
    nama: str
    deskripsi: Optional[str] = None
    tanggal_mulai: datetime
    tanggal_selesai: Optional[datetime] = None
    status: str = "active"
    lokasi: Optional[str] = None


class KegiatanCreate(KegiatanBase):
    program_id: int


class KegiatanUpdate(BaseModel):
    nama: Optional[str] = None
    deskripsi: Optional[str] = None
    tanggal_mulai: Optional[datetime] = None
    tanggal_selesai: Optional[datetime] = None
    status: Optional[str] = None
    lokasi: Optional[str] = None


class KegiatanResponse(KegiatanBase):
    id: int
    program_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KegiatanDetailResponse(KegiatanResponse):
    pass
