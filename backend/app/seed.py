from datetime import date
from app import auth, models
from app.database import SessionLocal

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_ADMIN_FULLNAME = "Administrator"


def seed_default_data():
    db = SessionLocal()
    try:
        if db.query(models.User).count() == 0:
            admin = models.User(
                username=DEFAULT_ADMIN_USERNAME,
                hashed_password=auth.hash_password(DEFAULT_ADMIN_PASSWORD),
                nama_lengkap=DEFAULT_ADMIN_FULLNAME,
                role="admin",
                is_active=True,
            )
            db.add(admin)
            db.flush()

            members = [
                models.User(username="ahmad", hashed_password=auth.hash_password("member123"),
                            nama_lengkap="Ahmad Fauzi", role="member", nis="M001",
                            kwaran="Jawa Barat", kwarcab="Kwartir Cabang Depok", phone="08111111111"),
                models.User(username="siti", hashed_password=auth.hash_password("member123"),
                            nama_lengkap="Siti Nurhaliza", role="member", nis="M002",
                            kwaran="Jawa Barat", kwarcab="Kwartir Cabang Depok", phone="08222222222"),
                models.User(username="budi", hashed_password=auth.hash_password("member123"),
                            nama_lengkap="Budi Santoso", role="member", nis="M003",
                            kwaran="Jawa Barat", kwarcab="Kwartir Cabang Cimahi", phone="08333333333"),
                models.User(username="dewi", hashed_password=auth.hash_password("member123"),
                            nama_lengkap="Dewi Lestari", role="member", nis="M004",
                            kwaran="Jawa Barat", kwarcab="Kwartir Cabang Pangandaran", phone="08444444444"),
            ]
            db.add_all(members)
            db.flush()

            badges = [
                models.Badge(code="BD001", name="Penggalang Ramu", description="Badge dasar untuk penggalang",
                             category="Umum", level="dasar", requirements="Mengikuti pendidikan dasar pramuka", created_by=admin.id),
                models.Badge(code="BD002", name="Penggalang Rakit", description="Badge tingkat madya",
                             category="Umum", level="madya", requirements="Memiliki badge Penggalang Ramu", created_by=admin.id),
                models.Badge(code="BD003", name="Penggalang Terap", description="Badge tingkat laksana",
                             category="Umum", level="laksana", requirements="Memiliki badge Penggalang Rakit", created_by=admin.id),
                models.Badge(code="BD004", name="Penegak Garuda", description="Badge tertinggi penegak",
                             category="Umum", level="garuda", requirements="Memiliki badge Penegak Terap", created_by=admin.id),
                models.Badge(code="BD005", name="Pandega Wira", description="Badge pandega tingkat wira",
                             category="Umum", level="pandega", requirements="Memiliki badge Pandega Sakti", created_by=admin.id),
            ]
            db.add_all(badges)
            db.flush()

            tkks = [
                models.TKK(code="TKK001", name="Knot & Tali Dasar", description="Menguasai ikatan dasar pramuka",
                           category="Keterampilan", bidang="Pionering", level="dasar", created_by=admin.id),
                models.TKK(code="TKK002", name="Navigasi Kompas", description="Menggunakan kompas dan peta",
                           category="Keterampilan", bidang="Navigasi", level="dasar", created_by=admin.id),
                models.TKK(code="TKK003", name="Pertolongan Pertama", description="Dasar-dasar P3K",
                           category="Kesehatan", bidang="P3K", level="dasar", created_by=admin.id),
                models.TKK(code="TKK004", name="Memasak Lapangan", description="Memasak dengan peralatan minim",
                           category="Keterampilan", bidang="Kepramukaan", level="madya", created_by=admin.id),
                models.TKK(code="TKK005", name="Komunikasi Radio", description="Operasi handy talky",
                           category="Teknologi", bidang="Komunikasi", level="madya", created_by=admin.id),
                models.TKK(code="TKK006", name="Pionering Lanjut", description="Bangun struktur kompleks",
                           category="Keterampilan", bidang="Pionering", level="laksana", created_by=admin.id),
            ]
            db.add_all(tkks)
            db.flush()

            certs = [
                models.Certificate(code="CERT001", name="Kursus Dasar Kepramukaan (KDK)",
                                   description="Kursus wajib untuk pengurus", issuing_authority="Kwartir Nasional",
                                   certificate_type="kursus", level="nasional",
                                   valid_from=date(2024, 1, 1), valid_until=date(2029, 1, 1), created_by=admin.id),
                models.Certificate(code="CERT002", name="Kursus Kepemimpinan Tingkat Dasar (KKTD)",
                                   description="Kursus kepemimpinan dasar", issuing_authority="Kwartir Provinsi",
                                   certificate_type="kursus", level="provinsi",
                                   valid_from=date(2024, 1, 1), valid_until=date(2029, 1, 1), created_by=admin.id),
                models.Certificate(code="CERT003", name="Pelatihan P3K Pramuka",
                                   description="Pelatihan pertolongan pertama", issuing_authority="Kwartir Cabang",
                                   certificate_type="pelatihan", level="kabupaten",
                                   valid_from=date(2024, 1, 1), valid_until=date(2026, 1, 1), created_by=admin.id),
                models.Certificate(code="CERT004", name="Seminar Nasional Kepramukaan",
                                   description="Seminar tahunan nasional", issuing_authority="Kwartir Nasional",
                                   certificate_type="seminar", level="nasional",
                                   valid_from=date(2024, 8, 1), valid_until=date(2025, 8, 1), created_by=admin.id),
                models.Certificate(code="CERT005", name="Workshop Keterampilan Hidup",
                                   description="Workshop life skills", issuing_authority="Kwartir Cabang",
                                   certificate_type="workshop", level="lokal",
                                   valid_from=date(2024, 1, 1), valid_until=date(2025, 1, 1), created_by=admin.id),
            ]
            db.add_all(certs)
            db.flush()

            achievements = [
                models.Achievement(code="ACH001", title="Juara 1 Lomba Pionering Kabupaten",
                                   description="Membangun menara pionering tertinggi", achievement_type="competition",
                                   category="Pionering", level="kabupaten", points=100,
                                   event_date=date(2024, 3, 15), event_name="Lomba Pionering Tingkat Kabupaten",
                                   organizer="Kwartir Kabupaten", created_by=admin.id),
                models.Achievement(code="ACH002", title="Juara 2 Lomba Marching Band Provinsi",
                                   description="Penampilan marching band terbaik", achievement_type="competition",
                                   category="Seni", level="provinsi", points=80,
                                   event_date=date(2024, 5, 20), event_name="Festival Marching Band Provinsi",
                                   organizer="Kwartir Provinsi", created_by=admin.id),
                models.Achievement(code="ACH003", title="Pengabdian Masyarakat Ramadan",
                                   description="Bagi-bagi takjil dan sembako", achievement_type="service",
                                   category="Sosial", level="lokal", points=50,
                                   event_date=date(2024, 4, 10), event_name="Aksi Peduli Ramadan",
                                   organizer="Kwartir Cabang", created_by=admin.id),
                models.Achievement(code="ACH004", title="Ketua Panitia Jambore Cabang",
                                   description="Mengelola acara jambore 3 hari", achievement_type="leadership",
                                   category="Kepanitiaan", level="kabupaten", points=90,
                                   event_date=date(2024, 6, 1), event_name="Jambore Pramuka Tingkat Cabang",
                                   organizer="Kwartir Cabang", created_by=admin.id),
                models.Achievement(code="ACH005", title="Wakil Ketua Kwarcab",
                                   description="Memimpin organisasi tingkat cabang", achievement_type="leadership",
                                   category="Organisasi", level="kabupaten", points=120,
                                   event_date=date(2024, 1, 1), event_name="Rapat Pleno Tahunan",
                                   organizer="Kwartir Cabang", created_by=admin.id),
            ]
            db.add_all(achievements)
            db.flush()

            member_achievements = [
                models.MemberAchievement(user_id=members[0].id, achievement_type="badge", achievement_id=badges[0].id,
                                         earned_date=date(2024, 2, 1), verified_by=admin.id, verified_at=date(2024, 2, 1), status="verified", notes="Lulus ujian badge"),
                models.MemberAchievement(user_id=members[0].id, achievement_type="badge", achievement_id=badges[1].id,
                                         earned_date=date(2024, 4, 15), verified_by=admin.id, verified_at=date(2024, 4, 15), status="verified", notes="Lulus ujian badge"),
                models.MemberAchievement(user_id=members[0].id, achievement_type="tkk", achievement_id=tkks[0].id,
                                         earned_date=date(2024, 3, 1), verified_by=admin.id, verified_at=date(2024, 3, 1), status="verified", notes="Lulus ujian TKK"),
                models.MemberAchievement(user_id=members[0].id, achievement_type="certificate", achievement_id=certs[0].id,
                                         earned_date=date(2024, 1, 15), verified_by=admin.id, verified_at=date(2024, 1, 15), status="verified", notes="Lulus KDK"),
                models.MemberAchievement(user_id=members[0].id, achievement_type="achievement", achievement_id=achievements[0].id,
                                         earned_date=date(2024, 3, 15), verified_by=admin.id, verified_at=date(2024, 3, 15), status="verified", notes="Juara 1"),

                models.MemberAchievement(user_id=members[1].id, achievement_type="badge", achievement_id=badges[0].id,
                                         earned_date=date(2024, 1, 15), verified_by=admin.id, verified_at=date(2024, 1, 15), status="verified", notes="Lulus ujian badge"),
                models.MemberAchievement(user_id=members[1].id, achievement_type="tkk", achievement_id=tkks[0].id,
                                         earned_date=date(2024, 2, 1), verified_by=admin.id, verified_at=date(2024, 2, 1), status="verified", notes="Lulus ujian TKK"),
                models.MemberAchievement(user_id=members[1].id, achievement_type="tkk", achievement_id=tkks[2].id,
                                         earned_date=date(2024, 4, 1), verified_by=admin.id, verified_at=date(2024, 4, 1), status="verified", notes="Lulus ujian TKK"),
                models.MemberAchievement(user_id=members[1].id, achievement_type="certificate", achievement_id=certs[0].id,
                                         earned_date=date(2024, 1, 10), verified_by=admin.id, verified_at=date(2024, 1, 10), status="verified", notes="Lulus KDK"),
                models.MemberAchievement(user_id=members[1].id, achievement_type="certificate", achievement_id=certs[2].id,
                                         earned_date=date(2024, 2, 15), verified_by=admin.id, verified_at=date(2024, 2, 15), status="verified", notes="Lulus P3K"),

                models.MemberAchievement(user_id=members[2].id, achievement_type="badge", achievement_id=badges[0].id,
                                         earned_date=date(2024, 3, 1), verified_by=admin.id, verified_at=date(2024, 3, 1), status="verified", notes="Lulus ujian badge"),
                models.MemberAchievement(user_id=members[2].id, achievement_type="tkk", achievement_id=tkks[1].id,
                                         earned_date=date(2024, 4, 15), verified_by=admin.id, verified_at=date(2024, 4, 15), status="verified", notes="Lulus ujian TKK"),
                models.MemberAchievement(user_id=members[2].id, achievement_type="certificate", achievement_id=certs[0].id,
                                         earned_date=date(2024, 2, 1), verified_by=admin.id, verified_at=date(2024, 2, 1), status="verified", notes="Lulus KDK"),
                models.MemberAchievement(user_id=members[2].id, achievement_type="achievement", achievement_id=achievements[0].id,
                                         earned_date=date(2024, 3, 15), verified_by=admin.id, verified_at=date(2024, 3, 15), status="verified", notes="Juara 1"),

                models.MemberAchievement(user_id=members[3].id, achievement_type="badge", achievement_id=badges[0].id,
                                         earned_date=date(2024, 1, 20), verified_by=admin.id, verified_at=date(2024, 1, 20), status="verified", notes="Lulus ujian badge"),
                models.MemberAchievement(user_id=members[3].id, achievement_type="badge", achievement_id=badges[1].id,
                                         earned_date=date(2024, 5, 1), verified_by=admin.id, verified_at=date(2024, 5, 1), status="verified", notes="Lulus ujian badge"),
                models.MemberAchievement(user_id=members[3].id, achievement_type="tkk", achievement_id=tkks[0].id,
                                         earned_date=date(2024, 2, 15), verified_by=admin.id, verified_at=date(2024, 2, 15), status="verified", notes="Lulus ujian TKK"),
                models.MemberAchievement(user_id=members[3].id, achievement_type="certificate", achievement_id=certs[0].id,
                                         earned_date=date(2024, 1, 10), verified_by=admin.id, verified_at=date(2024, 1, 10), status="verified", notes="Lulus KDK"),
                models.MemberAchievement(user_id=members[3].id, achievement_type="certificate", achievement_id=certs[1].id,
                                         earned_date=date(2024, 3, 1), verified_by=admin.id, verified_at=date(2024, 3, 1), status="verified", notes="Lulus KKTD"),
                models.MemberAchievement(user_id=members[3].id, achievement_type="achievement", achievement_id=achievements[1].id,
                                         earned_date=date(2024, 5, 20), verified_by=admin.id, verified_at=date(2024, 5, 20), status="verified", notes="Juara 2"),
                models.MemberAchievement(user_id=members[3].id, achievement_type="achievement", achievement_id=achievements[4].id,
                                         earned_date=date(2024, 1, 1), verified_by=admin.id, verified_at=date(2024, 1, 1), status="verified", notes="Wakil Ketua"),
            ]
            db.add_all(member_achievements)

            db.commit()
            print("Database seeded: 1 admin, 4 members, 5 badges, 6 TKK, 5 certificates, 5 achievements, 26 member_achievements")
    except Exception as e:
        db.rollback()
        print(f"Seed error: {e}")
    finally:
        db.close()
