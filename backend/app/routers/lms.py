from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/lms", tags=["lms"])


@router.get("/trainings")
def list_trainings(
    search: Optional[str] = Query(None, description="Cari berdasarkan judul pelatihan"),
    page: int = Query(1, ge=1, description="Halaman saat ini"),
    limit: int = Query(6, ge=1, le=50, description="Jumlah item per halaman"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Training).order_by(models.Training.id.desc())

    if search:
        query = query.filter(models.Training.title.ilike(f"%{search}%"))

    total = query.count()
    total_pages = (total + limit - 1) // limit
    items = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }


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


@router.get("/trainings/{training_id}/quiz", response_model=schemas.QuizOut)
def get_quiz(training_id: int, db: Session = Depends(get_db)):
    quiz = db.query(models.Quiz).filter(models.Quiz.training_id == training_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Kuis tidak ditemukan untuk pelatihan ini")
    return quiz


@router.get("/quizzes/{quiz_id}/questions", response_model=List[schemas.QuizQuestionOut])
def list_quiz_questions(quiz_id: int, db: Session = Depends(get_db)):
    questions = db.query(models.QuizQuestion).filter(models.QuizQuestion.quiz_id == quiz_id).all()
    if not questions:
        raise HTTPException(status_code=404, detail="Soal kuis tidak ditemukan")
    return questions

@router.post("/quizzes/{quiz_id}/submit", response_model=schemas.QuizSubmitResponse)
def submit_quiz(
    quiz_id: int,
    payload: schemas.QuizSubmitRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Kuis tidak ditemukan")
        
    training = db.query(models.Training).filter(models.Training.id == quiz.training_id).first()
    enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.user_id == current_user.id,
        models.Enrollment.training_id == training.id
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=400, detail="Anda belum terdaftar di pelatihan ini")

    questions = db.query(models.QuizQuestion).filter(models.QuizQuestion.quiz_id == quiz_id).all()
    question_map = {q.id: q for q in questions}
    
    total_score = 0
    max_score = sum(q.score_weight for q in questions)
    
    for ans in payload.answers:
        q = question_map.get(ans.question_id)
        if q and q.correct_answer == ans.answer:
            total_score += q.score_weight
            
    # Normalize score to 100
    final_score = int((total_score / max_score) * 100) if max_score > 0 else 0
    passed = final_score >= training.passing_grade
    
    enrollment.progress_percentage = final_score
    enrollment.status = "Lulus" if passed else "Gagal"
    db.commit()
    
    return {
        "total_score": final_score,
        "passed": passed,
        "status": enrollment.status,
        "message": "Selamat, Anda Lulus!" if passed else "Maaf, Anda belum memenuhi nilai kelulusan."
    }


@router.get("/enrollments/{enrollment_id}/certificate")
def get_certificate(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.id == enrollment_id,
        models.Enrollment.user_id == current_user.id
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=404, detail="Data pendaftaran tidak ditemukan")
        
    if enrollment.status != "Lulus":
        raise HTTPException(status_code=400, detail="Anda belum lulus pelatihan ini")
        
    training = db.query(models.Training).filter(models.Training.id == enrollment.training_id).first()
    
    # In a real app, this might generate a PDF or an image.
    # For now, we return certificate metadata.
    return {
        "certificate_id": f"KWARCAB-KBB-{enrollment.id}-{current_user.id}",
        "issued_to": current_user.nama_lengkap,
        "training_title": training.title,
        "issue_date": enrollment.enrolled_at.strftime("%Y-%m-%d"),
        "status": "Valid",
        "message": "Sertifikat ini sah dan diterbitkan oleh Kwarcab KBB."
    }
