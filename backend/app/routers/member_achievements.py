from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_, or_

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user, get_current_admin

router = APIRouter(prefix="/member-achievements", tags=["member-achievements"])


def _get_user_or_404(db: Session, user_id: int) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Anggota tidak ditemukan")
    return user


def _get_achievement_name(ach_type: str, ach_id: int, db: Session):
    if ach_type == "badge":
        item = db.query(models.Badge).filter(models.Badge.id == ach_id).first()
        return item.name if item else None, item.level if item else None, None
    elif ach_type == "tkk":
        item = db.query(models.TKK).filter(models.TKK.id == ach_id).first()
        return item.name if item else None, item.bidang if item else None, None
    elif ach_type == "certificate":
        item = db.query(models.Certificate).filter(models.Certificate.id == ach_id).first()
        return item.name if item else None, item.certificate_type if item else None, None
    elif ach_type == "achievement":
        item = db.query(models.Achievement).filter(models.Achievement.id == ach_id).first()
        return item.title if item else None, None, item.points if item else 0
    return None, None, 0


def _enrich_member_achievement(ma, db: Session):
    name, sub1, points = _get_achievement_name(ma.achievement_type, ma.achievement_id, db)
    user = db.query(models.User).filter(models.User.id == ma.user_id).first()
    result = {
        "id": ma.id,
        "user_id": ma.user_id,
        "achievement_type": ma.achievement_type,
        "achievement_id": ma.achievement_id,
        "earned_date": ma.earned_date,
        "verified_by": ma.verified_by,
        "verified_at": ma.verified_at,
        "status": ma.status,
        "notes": ma.notes,
        "evidence_url": ma.evidence_url,
        "created_at": ma.created_at,
        "member_name": user.nama_lengkap if user else None,
    }
    if ma.achievement_type == "badge":
        result["badge_name"] = name
        result["badge_level"] = sub1
    elif ma.achievement_type == "tkk":
        result["tkk_name"] = name
        result["tkk_bidang"] = sub1
    elif ma.achievement_type == "certificate":
        result["cert_name"] = name
        result["cert_type"] = sub1
    elif ma.achievement_type == "achievement":
        result["ach_title"] = name
        result["ach_points"] = points
    return result


# ─── Admin: award achievement ───────────────────────────
@router.post("/award", response_model=schemas.MemberAchievementOut, status_code=status.HTTP_201_CREATED)
def award_achievement(
    payload: schemas.MemberAchievementCreate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin),
):
    _get_user_or_404(db, payload.user_id)

    valid_types = ["badge", "tkk", "certificate", "achievement"]
    if payload.achievement_type not in valid_types:
        raise HTTPException(status_code=400, detail="Tipe pencapaian tidak valid")

    existing = (
        db.query(models.MemberAchievement)
        .filter(
            models.MemberAchievement.user_id == payload.user_id,
            models.MemberAchievement.achievement_type == payload.achievement_type,
            models.MemberAchievement.achievement_id == payload.achievement_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Anggota sudah memiliki pencapaian ini")

    ma = models.MemberAchievement(
        user_id=payload.user_id,
        achievement_type=payload.achievement_type,
        achievement_id=payload.achievement_id,
        earned_date=payload.earned_date,
        verified_by=admin.id,
        verified_at=datetime.utcnow(),
        status="verified",
        notes=payload.notes,
        evidence_url=payload.evidence_url,
    )
    db.add(ma)
    db.commit()
    db.refresh(ma)
    return _enrich_member_achievement(ma, db)


# ─── Admin: verify pending achievement ──────────────────
@router.put("/{ma_id}/verify", response_model=schemas.MemberAchievementOut)
def verify_achievement(
    ma_id: int,
    status_val: str = Query(..., alias="status"),
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin),
):
    ma = db.query(models.MemberAchievement).filter(models.MemberAchievement.id == ma_id).first()
    if not ma:
        raise HTTPException(status_code=404, detail="Pencapaian tidak ditemukan")
    ma.status = status_val
    ma.verified_by = admin.id
    ma.verified_at = datetime.utcnow()
    db.commit()
    db.refresh(ma)
    return _enrich_member_achievement(ma, db)


# ─── Admin: update achievement ──────────────────────────
@router.put("/{ma_id}", response_model=schemas.MemberAchievementOut)
def update_member_achievement(
    ma_id: int,
    payload: schemas.MemberAchievementUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    ma = db.query(models.MemberAchievement).filter(models.MemberAchievement.id == ma_id).first()
    if not ma:
        raise HTTPException(status_code=404, detail="Pencapaian tidak ditemukan")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(ma, k, v)
    db.commit()
    db.refresh(ma)
    return _enrich_member_achievement(ma, db)


# ─── Admin: delete achievement ──────────────────────────
@router.delete("/{ma_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member_achievement(
    ma_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    ma = db.query(models.MemberAchievement).filter(models.MemberAchievement.id == ma_id).first()
    if not ma:
        raise HTTPException(status_code=404, detail="Pencapaian tidak ditemukan")
    db.delete(ma)
    db.commit()


# ─── Admin: list all member achievements ────────────────
@router.get("", response_model=List[schemas.MemberAchievementOut])
def list_all_member_achievements(
    user_id: Optional[int] = None,
    achievement_type: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    q = db.query(models.MemberAchievement)
    if user_id:
        q = q.filter(models.MemberAchievement.user_id == user_id)
    if achievement_type:
        q = q.filter(models.MemberAchievement.achievement_type == achievement_type)
    if status_filter:
        q = q.filter(models.MemberAchievement.status == status_filter)
    items = q.order_by(models.MemberAchievement.earned_date.desc()).offset(
        (page - 1) * limit
    ).limit(limit).all()
    return [_enrich_member_achievement(m, db) for m in items]


# ─── Member: view own achievements ──────────────────────
@router.get("/my-achievements", response_model=List[schemas.MemberAchievementOut])
def get_my_achievements(
    achievement_type: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    q = db.query(models.MemberAchievement).filter(
        models.MemberAchievement.user_id == current_user.id
    )
    if achievement_type:
        q = q.filter(models.MemberAchievement.achievement_type == achievement_type)
    if status_filter:
        q = q.filter(models.MemberAchievement.status == status_filter)
    items = q.order_by(models.MemberAchievement.earned_date.desc()).offset(
        (page - 1) * limit
    ).limit(limit).all()
    return [_enrich_member_achievement(m, db) for m in items]


# ─── Member: get own dashboard stats ────────────────────
@router.get("/my-stats", response_model=schemas.DashboardStats)
def get_my_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    q = db.query(models.MemberAchievement).filter(
        models.MemberAchievement.user_id == current_user.id,
        models.MemberAchievement.status == "verified",
    )
    all_items = q.all()
    total_points = 0
    for item in all_items:
        if item.achievement_type == "achievement":
            ach = db.query(models.Achievement).filter(models.Achievement.id == item.achievement_id).first()
            if ach:
                total_points += ach.points or 0
    return schemas.DashboardStats(
        total=len(all_items),
        badges_count=sum(1 for i in all_items if i.achievement_type == "badge"),
        tkk_count=sum(1 for i in all_items if i.achievement_type == "tkk"),
        certificates_count=sum(1 for i in all_items if i.achievement_type == "certificate"),
        achievements_count=sum(1 for i in all_items if i.achievement_type == "achievement"),
        total_points=total_points,
    )


# ─── Leaderboard ────────────────────────────────────────
@router.get("/leaderboard", response_model=List[schemas.LeaderboardEntry])
def get_leaderboard(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    kwarcab: Optional[str] = None,
    db: Session = Depends(get_db),
):
    user_q = db.query(models.User).filter(
        models.User.role.in_(["member", "admin"]),
        models.User.is_active == True,
    )
    if kwarcab:
        user_q = user_q.filter(models.User.kwarcab == kwarcab)
    users = user_q.all()

    results = []
    for user in users:
        achievements = (
            db.query(models.MemberAchievement)
            .filter(
                models.MemberAchievement.user_id == user.id,
                models.MemberAchievement.status == "verified",
            )
            .all()
        )
        badge_count = sum(1 for a in achievements if a.achievement_type == "badge")
        tkk_count = sum(1 for a in achievements if a.achievement_type == "tkk")
        cert_count = sum(1 for a in achievements if a.achievement_type == "certificate")
        ach_count = sum(1 for a in achievements if a.achievement_type == "achievement")

        total_points = 0
        for a in achievements:
            if a.achievement_type == "achievement":
                ach = db.query(models.Achievement).filter(models.Achievement.id == a.achievement_id).first()
                if ach:
                    total_points += ach.points or 0

        results.append(schemas.LeaderboardEntry(
            id=user.id,
            full_name=user.nama_lengkap,
            nis=user.nis,
            kwarcab=user.kwarcab,
            badge_count=badge_count,
            tkk_count=tkk_count,
            certificate_count=cert_count,
            achievement_count=ach_count,
            total_points=total_points,
            total_achievements=len(achievements),
        ))

    results.sort(key=lambda x: (-x.total_points, -x.total_achievements))
    return results[offset: offset + limit]
