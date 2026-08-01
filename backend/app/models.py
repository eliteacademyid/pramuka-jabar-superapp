from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.database import Base

ROLES = ("admin", "staff")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nama_lengkap = Column(String, nullable=False)
    role = Column(String, nullable=False, default="staff")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Training(Base):
    __tablename__ = "trainings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    passing_grade = Column(Integer, default=70)
    status = Column(String, default="Draft")
    created_at = Column(DateTime, default=datetime.utcnow)

class TrainingMaterial(Base):
    __tablename__ = "training_materials"

    id = Column(Integer, primary_key=True, index=True)
    training_id = Column(Integer, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=True)
    media_url = Column(String, nullable=True)
    order = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    training_id = Column(Integer, index=True)
    title = Column(String, nullable=False)
    time_limit_minutes = Column(Integer, default=30)
    created_at = Column(DateTime, default=datetime.utcnow)


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, index=True)
    question_text = Column(String, nullable=False)
    options = Column(String, nullable=False) # JSON string
    correct_answer = Column(String, nullable=False)
    score_weight = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    training_id = Column(Integer, index=True)
    progress_percentage = Column(Integer, default=0)
    status = Column(String, default="Enrolled") # Enrolled, Completed, Dropped
    enrolled_at = Column(DateTime, default=datetime.utcnow)




