from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/lms", tags=["lms"])


@router.get("/trainings", response_model=List[schemas.TrainingOut])
def list_trainings(db: Session = Depends(get_db)):
    return db.query(models.Training).order_by(models.Training.id.desc()).all()


@router.get("/trainings/{training_id}/materials", response_model=List[schemas.TrainingMaterialOut])
def list_training_materials(training_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.TrainingMaterial)
        .filter(models.TrainingMaterial.training_id == training_id)
        .order_by(models.TrainingMaterial.order.asc())
        .all()
    )


@router.post("/trainings/{training_id}/enroll", response_model=schemas.EnrollmentOut, status_code=status.HTTP_201_CREATED)
def enroll_training(
    training_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    training = db.query(models.Training).filter(models.Training.id == training_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="Training tidak ditemukan")
        
    existing_enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.user_id == current_user.id,
        models.Enrollment.training_id == training_id
    ).first()
    
    if existing_enrollment:
        raise HTTPException(status_code=400, detail="Anda sudah terdaftar di pelatihan ini")
        
    enrollment = models.Enrollment(
        user_id=current_user.id,
        training_id=training_id,
        progress_percentage=0,
        status="Enrolled"
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.get("/enrollments/me", response_model=List[schemas.EnrollmentOut])
def get_my_enrollments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Enrollment).filter(models.Enrollment.user_id == current_user.id).order_by(models.Enrollment.enrolled_at.desc()).all()
