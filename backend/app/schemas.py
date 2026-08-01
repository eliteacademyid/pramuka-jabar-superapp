from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel

from app.models import ROLES


# ─── Auth ───────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# ─── User ───────────────────────────────────────────────
class UserCreate(BaseModel):
    username: str
    password: str
    nama_lengkap: str
    role: str = "member"
    nis: Optional[str] = None
    kwaran: Optional[str] = None
    kwarcab: Optional[str] = None
    phone: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    nama_lengkap: Optional[str] = None
    role: Optional[str] = None
    nis: Optional[str] = None
    kwaran: Optional[str] = None
    kwarcab: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    username: str
    nama_lengkap: str
    role: str
    nis: Optional[str] = None
    kwaran: Optional[str] = None
    kwarcab: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Badge ──────────────────────────────────────────────
class BadgeCreate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    level: str
    image_url: Optional[str] = None
    requirements: Optional[str] = None


class BadgeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = None
    image_url: Optional[str] = None
    requirements: Optional[str] = None
    is_active: Optional[bool] = None


class BadgeOut(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    level: str
    image_url: Optional[str] = None
    requirements: Optional[str] = None
    is_active: bool
    created_by: Optional[int] = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── TKK ────────────────────────────────────────────────
class TKKCreate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    bidang: str
    level: str
    image_url: Optional[str] = None
    requirements: Optional[str] = None


class TKKUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    bidang: Optional[str] = None
    level: Optional[str] = None
    image_url: Optional[str] = None
    requirements: Optional[str] = None
    is_active: Optional[bool] = None


class TKKOut(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    bidang: str
    level: str
    image_url: Optional[str] = None
    requirements: Optional[str] = None
    is_active: bool
    created_by: Optional[int] = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Certificate ────────────────────────────────────────
class CertificateCreate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    issuing_authority: Optional[str] = None
    certificate_type: str
    level: str
    image_url: Optional[str] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None


class CertificateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    issuing_authority: Optional[str] = None
    certificate_type: Optional[str] = None
    level: Optional[str] = None
    image_url: Optional[str] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    is_active: Optional[bool] = None


class CertificateOut(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None
    issuing_authority: Optional[str] = None
    certificate_type: str
    level: str
    image_url: Optional[str] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    is_active: bool
    created_by: Optional[int] = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Achievement ────────────────────────────────────────
class AchievementCreate(BaseModel):
    code: str
    title: str
    description: Optional[str] = None
    achievement_type: str
    category: Optional[str] = None
    level: str
    points: int = 0
    image_url: Optional[str] = None
    event_date: Optional[date] = None
    event_name: Optional[str] = None
    organizer: Optional[str] = None


class AchievementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    achievement_type: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = None
    points: Optional[int] = None
    image_url: Optional[str] = None
    event_date: Optional[date] = None
    event_name: Optional[str] = None
    organizer: Optional[str] = None
    is_active: Optional[bool] = None


class AchievementOut(BaseModel):
    id: int
    code: str
    title: str
    description: Optional[str] = None
    achievement_type: str
    category: Optional[str] = None
    level: str
    points: int
    image_url: Optional[str] = None
    event_date: Optional[date] = None
    event_name: Optional[str] = None
    organizer: Optional[str] = None
    is_active: bool
    created_by: Optional[int] = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Member Achievement ─────────────────────────────────
class MemberAchievementCreate(BaseModel):
    user_id: int
    achievement_type: str
    achievement_id: int
    earned_date: date
    notes: Optional[str] = None
    evidence_url: Optional[str] = None


class MemberAchievementUpdate(BaseModel):
    earned_date: Optional[date] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    evidence_url: Optional[str] = None


class MemberAchievementOut(BaseModel):
    id: int
    user_id: int
    achievement_type: str
    achievement_id: int
    earned_date: date
    verified_by: Optional[int] = None
    verified_at: Optional[datetime] = None
    status: str
    notes: Optional[str] = None
    evidence_url: Optional[str] = None
    created_at: datetime

    member_name: Optional[str] = None
    badge_name: Optional[str] = None
    badge_level: Optional[str] = None
    tkk_name: Optional[str] = None
    tkk_bidang: Optional[str] = None
    cert_name: Optional[str] = None
    cert_type: Optional[str] = None
    ach_title: Optional[str] = None
    ach_points: Optional[int] = None
    model_config = {"from_attributes": True}


# ─── Leaderboard ────────────────────────────────────────
class LeaderboardEntry(BaseModel):
    id: int
    full_name: str
    nis: Optional[str] = None
    kwarcab: Optional[str] = None
    badge_count: int = 0
    tkk_count: int = 0
    certificate_count: int = 0
    achievement_count: int = 0
    total_points: int = 0
    total_achievements: int = 0


# ─── Dashboard Stats ────────────────────────────────────
class DashboardStats(BaseModel):
    total: int = 0
    badges_count: int = 0
    tkk_count: int = 0
    certificates_count: int = 0
    achievements_count: int = 0
    total_points: int = 0
