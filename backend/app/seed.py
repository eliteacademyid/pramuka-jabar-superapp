from app import auth, models
from app.database import SessionLocal

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_ADMIN_FULLNAME = "Administrator"


def seed_default_admin():
    db = SessionLocal()
    try:
        if db.query(models.User).count() == 0:
            db.add(
                models.User(
                    username=DEFAULT_ADMIN_USERNAME,
                    hashed_password=auth.hash_password(DEFAULT_ADMIN_PASSWORD),
                    nama_lengkap=DEFAULT_ADMIN_FULLNAME,
                    role="admin",
                    is_active=True,
                )
            )
            # Add a dummy staff user for testing LMS
            db.add(
                models.User(
                    username="peserta1",
                    hashed_password=auth.hash_password("peserta123"),
                    nama_lengkap="Peserta Dummy (Staff)",
                    role="staff",
                    is_active=True,
                )
            )
            db.commit()
    finally:
        db.close()


def seed_lms_dummy_data():
    db = SessionLocal()
    try:
        # Check if dummy training already exists
        if db.query(models.Training).count() == 0:
            # 1. Create Training
            training = models.Training(
                title="Pramuka Garuda Tingkat Siaga",
                description="Pelatihan dasar untuk mencapai tingkatan Pramuka Garuda Siaga.",
                status="Published",
                passing_grade=75
            )
            db.add(training)
            db.commit()
            db.refresh(training)

            # 2. Create Training Materials
            material1 = models.TrainingMaterial(
                training_id=training.id,
                title="Modul 1: Sejarah Pramuka Garuda",
                content="Pramuka Garuda merupakan tingkatan tertinggi dalam setiap golongan Pramuka (Siaga, Penggalang, Penegak, Pandega).",
                order=1
            )
            material2 = models.TrainingMaterial(
                training_id=training.id,
                title="Modul 2: Syarat-syarat Kecakapan",
                content="Untuk mencapai tingkat ini, peserta didik harus telah menyelesaikan SKU tingkat akhir di golongannya.",
                order=2
            )
            db.add_all([material1, material2])
            db.commit()

            # 3. Create Quiz
            quiz = models.Quiz(
                training_id=training.id,
                title="Evaluasi Akhir Pramuka Garuda Siaga",
                time_limit_minutes=15
            )
            db.add(quiz)
            db.commit()
            db.refresh(quiz)

            # 4. Create Quiz Questions
            question1 = models.QuizQuestion(
                quiz_id=quiz.id,
                question_text="Apa tingkatan tertinggi dalam golongan Pramuka Siaga sebelum bisa menjadi Garuda?",
                options='["Siaga Mula", "Siaga Bantu", "Siaga Tata", "Siaga Utama"]',
                correct_answer="Siaga Tata",
                score_weight=50
            )
            question2 = models.QuizQuestion(
                quiz_id=quiz.id,
                question_text="Berapa lama usia maksimal seorang Pramuka Siaga?",
                options='["10 tahun", "11 tahun", "15 tahun", "18 tahun"]',
                correct_answer="10 tahun",
                score_weight=50
            )
            db.add_all([question1, question2])
            db.commit()
    finally:
        db.close()
