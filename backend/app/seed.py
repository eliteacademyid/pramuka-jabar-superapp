<<<<<<< HEAD
from datetime import datetime

=======
>>>>>>> b0b9cda (feat: initialize Vue 3 project with Vite)
from app import auth, models
from app.database import SessionLocal

DEFAULT_ADMIN_USERNAME = "admin"
<<<<<<< HEAD
DEFAULT_ADMIN_EMAIL = "admin@pramuka.com"
=======
>>>>>>> b0b9cda (feat: initialize Vue 3 project with Vite)
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_ADMIN_FULLNAME = "Administrator"


<<<<<<< HEAD
def seed_roles():
    """Create default roles"""
    db = SessionLocal()
    try:
        if db.query(models.Role).count() == 0:
            roles = [
                models.Role(name="admin", description="Administrator role dengan akses penuh"),
                models.Role(name="staff", description="Staff role dengan akses terbatas"),
            ]
            db.add_all(roles)
            db.commit()
    finally:
        db.close()


def seed_default_admin():
    """Create default admin user"""
    db = SessionLocal()
    try:
        seed_roles()

        if db.query(models.User).filter(models.User.username == DEFAULT_ADMIN_USERNAME).first():
            return

        admin_role = db.query(models.Role).filter(models.Role.name == "admin").first()
        if not admin_role:
            seed_roles()
            admin_role = db.query(models.Role).filter(models.Role.name == "admin").first()

        admin_user = models.User(
            username=DEFAULT_ADMIN_USERNAME,
            email=DEFAULT_ADMIN_EMAIL,
            hashed_password=auth.hash_password(DEFAULT_ADMIN_PASSWORD),
            nama_lengkap=DEFAULT_ADMIN_FULLNAME,
            role_id=admin_role.id,
            is_active=True,
        )

        db.add(admin_user)
        db.commit()
        print("✓ Default admin user created successfully")
    except Exception as e:
        db.rollback()
        print(f"✗ Error seeding default admin: {e}")
    finally:
        db.close()


def seed_realisasi_laporan_approval():
    """Create sample realisasi, laporan, and approval data"""
    db = SessionLocal()
    try:
        if db.query(models.Realisasi).count() > 0:
            return

        organisasi = db.query(models.Organisasi).filter(models.Organisasi.nama == "Organisasi Pramuka Jawa Barat").first()
        if not organisasi:
            organisasi = models.Organisasi(
                nama="Organisasi Pramuka Jawa Barat",
                alamat="Bandung",
                telepon="022-1234567",
                email="info@pramuka-jabar.id",
                is_active=True,
            )
            db.add(organisasi)
            db.commit()
            db.refresh(organisasi)

        admin_user = db.query(models.User).filter(models.User.username == DEFAULT_ADMIN_USERNAME).first()
        if not admin_user:
            seed_default_admin()
            admin_user = db.query(models.User).filter(models.User.username == DEFAULT_ADMIN_USERNAME).first()

        program = db.query(models.Program).filter(models.Program.nama == "Program Pemberdayaan Anggota").first()
        if not program:
            program = models.Program(
                nama="Program Pemberdayaan Anggota",
                deskripsi="Program peningkatan kapasitas keanggotaan",
                tahun=datetime.utcnow().year,
                status="active",
                creator_id=admin_user.id,
                organisasi_id=organisasi.id,
            )
            db.add(program)
            db.commit()
            db.refresh(program)

        kegiatan = db.query(models.Kegiatan).filter(models.Kegiatan.nama == "Latihan Kepemimpinan").first()
        if not kegiatan:
            kegiatan = models.Kegiatan(
                nama="Latihan Kepemimpinan",
                deskripsi="Latihan kepemimpinan untuk anggota muda",
                program_id=program.id,
                tanggal_mulai=datetime.utcnow(),
                tanggal_selesai=datetime.utcnow(),
                status="completed",
                lokasi="Bandung",
            )
            db.add(kegiatan)
            db.commit()
            db.refresh(kegiatan)

        realisasi = models.Realisasi(
            judul="Realisasi Latihan Kepemimpinan",
            deskripsi="Pelaksanaan pelatihan kepemimpinan untuk 50 anggota",
            target=50,
            realisasi=42,
            periode="Agustus 2026",
            status="approved",
            file_name="laporan-kepemimpinan.pdf",
            file_url="https://example.com/laporan-kepemimpinan.pdf",
            program_id=program.id,
            kegiatan_id=kegiatan.id,
            created_by_id=admin_user.id,
        )
        db.add(realisasi)
        db.commit()
        db.refresh(realisasi)

        laporan = models.Laporan(
            judul="Laporan Mingguan Latihan",
            periode="Agustus 2026",
            deskripsi="Ringkasan kegiatan dan realisasi minggu ini",
            status="approved",
            realisasi_id=realisasi.id,
            created_by_id=admin_user.id,
            approved_by_id=admin_user.id,
        )
        db.add(laporan)
        db.commit()
        db.refresh(laporan)

        approval = models.Approval(
            laporan_id=laporan.id,
            user_id=admin_user.id,
            status="approved",
            catatan="Disetujui sesuai target",
        )
        db.add(approval)
        db.commit()
        print("✓ Sample realisasi, laporan, and approval data created successfully")
    except Exception as e:
        db.rollback()
        print(f"✗ Error seeding realisasi data: {e}")
=======
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
            db.commit()
>>>>>>> b0b9cda (feat: initialize Vue 3 project with Vite)
    finally:
        db.close()
