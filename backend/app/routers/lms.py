from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

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

