from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_admin

router = APIRouter(prefix="/admin/lms", tags=["admin-lms"])


@router.post("/trainings", response_model=schemas.TrainingOut, status_code=status.HTTP_201_CREATED)
def create_training(
    payload: schemas.TrainingCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    training = models.Training(**payload.model_dump())
    db.add(training)
    db.commit()
    db.refresh(training)
    return training


@router.put("/trainings/{training_id}", response_model=schemas.TrainingOut)
def update_training(
    training_id: int,
    payload: schemas.TrainingUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    training = db.query(models.Training).filter(models.Training.id == training_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="Pelatihan tidak ditemukan")
    
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(training, key, value)
        
    db.commit()
    db.refresh(training)
    return training


@router.delete("/trainings/{training_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_training(
    training_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    training = db.query(models.Training).filter(models.Training.id == training_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="Pelatihan tidak ditemukan")
        
    db.delete(training)
    db.commit()


@router.post("/materials", response_model=schemas.TrainingMaterialOut, status_code=status.HTTP_201_CREATED)
def create_material(
    payload: schemas.TrainingMaterialCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    material = models.TrainingMaterial(**payload.model_dump())
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


@router.put("/materials/{material_id}", response_model=schemas.TrainingMaterialOut)
def update_material(
    material_id: int,
    payload: schemas.TrainingMaterialUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    material = db.query(models.TrainingMaterial).filter(models.TrainingMaterial.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Materi tidak ditemukan")
        
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(material, key, value)
        
    db.commit()
    db.refresh(material)
    return material


@router.delete("/materials/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    material = db.query(models.TrainingMaterial).filter(models.TrainingMaterial.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Materi tidak ditemukan")
        
    db.delete(material)
    db.commit()


@router.post("/quizzes", response_model=schemas.QuizOut, status_code=status.HTTP_201_CREATED)
def create_quiz(
    payload: schemas.QuizCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    # Check if training already has quiz
    existing = db.query(models.Quiz).filter(models.Quiz.training_id == payload.training_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Pelatihan ini sudah memiliki kuis")
        
    quiz = models.Quiz(**payload.model_dump())
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz


@router.post("/questions", response_model=schemas.QuizQuestionOut, status_code=status.HTTP_201_CREATED)
def create_question(
    payload: schemas.QuizQuestionCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    question = models.QuizQuestion(**payload.model_dump())
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@router.put("/questions/{question_id}", response_model=schemas.QuizQuestionOut)
def update_question(
    question_id: int,
    payload: schemas.QuizQuestionCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    question = db.query(models.QuizQuestion).filter(models.QuizQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Soal tidak ditemukan")
        
    for key, value in payload.model_dump().items():
        setattr(question, key, value)
        
    db.commit()
    db.refresh(question)
    return question


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    question = db.query(models.QuizQuestion).filter(models.QuizQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Soal tidak ditemukan")
        
    db.delete(question)
    db.commit()
