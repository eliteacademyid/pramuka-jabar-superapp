from decimal import Decimal

from app import auth, models
from app.database import SessionLocal
from app.services.common import ensure_wallet, unique_slug

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_ADMIN_FULLNAME = "Administrator"

SETTINGS_DEFAULT = {
    "COMMISSION_RATE": "5",
    "ONGKIR_TIER_A": "10000",
    "ONGKIR_TIER_B": "15000",
    "ONGKIR_TIER_C": "25000",
}

CATEGORIES_DEFAULT = [
    ("Makanan", "makanan"),
    ("Minuman", "minuman"),
    ("Kerajinan", "kerajinan"),
    ("Fashion", "fashion"),
    ("Jasa", "jasa"),
    ("Lainnya", "lainnya"),
]

DEMO_IMAGES = {
    "makanan": [
        "https://cdn.javascout.test/images/makanan-1.jpg",
        "https://cdn.javascout.test/images/makanan-2.jpg",
    ],
    "minuman": ["https://cdn.javascout.test/images/minuman-1.jpg"],
    "kerajinan": ["https://cdn.javascout.test/images/kerajinan-1.jpg"],
    "fashion": ["https://cdn.javascout.test/images/fashion-1.jpg"],
}


def _seed_settings(db):
    for key, value in SETTINGS_DEFAULT.items():
        if not db.get(models.Setting, key):
            db.add(models.Setting(key=key, value=value))


def _seed_categories(db):
    for name, slug in CATEGORIES_DEFAULT:
        if not db.query(models.Category).filter(models.Category.slug == slug).first():
            db.add(models.Category(name=name, slug=slug))
    db.flush()


def _seed_demo_data(db):
    """Data sintetis dummy — TIDAK mengandung data pribadi nyata (NFR-06)."""
    if db.query(models.User).filter(models.User.username == "member_budi").first():
        return

    member = models.User(
        username="member_budi",
        hashed_password=auth.hash_password("password123"),
        nama_lengkap="Budi Anggota Sintetis",
        email="member.budi@example.test",
        account_type="anggota",
        scout_number="SK-000-001",
        kwartir="Kwarcab Sintetis",
        golongan="Penggalang",
        role="member",
        is_active=True,
    )
    umum = models.User(
        username="siti_umum",
        hashed_password=auth.hash_password("password123"),
        nama_lengkap="Siti Pembeli Sintetis",
        email="siti@example.test",
        account_type="umum",
        role="member",
        is_active=True,
    )
    db.add_all([member, umum])
    db.flush()
    ensure_wallet(db, member)
    ensure_wallet(db, umum)

    kategori = {
        c.slug: c
        for c in db.query(models.Category).all()
    }

    toko = models.Store(
        owner_id=member.id,
        name="Toko UMKM Jaya",
        slug=unique_slug(db, models.Store, "Toko UMKM Jaya"),
        description="Toko sintetis UMKM lokal untuk demo JavaScout.",
        category_id=kategori["makanan"].id,
        city="Bandung",
        province="Jawa Barat",
        phone="0812-0000-0001",
        status="active",
    )
    db.add(toko)
    db.flush()

    produk = [
        (
            "Kue Kering Scout Cookies",
            "makanan",
            "120000",
            50,
            "toples",
            "active",
            37,
        ),
        (
            "Keripik Pisang Aneka Rasa",
            "makanan",
            "18000",
            120,
            "bungkus",
            "active",
            142,
        ),
        (
            "Es Kopi Gula Aren",
            "minuman",
            "15000",
            80,
            "cup",
            "active",
            95,
        ),
        (
            "Gelang Tali Kur Sintetis",
            "kerajinan",
            "25000",
            30,
            "pcs",
            "active",
            12,
        ),
        (
            "Tote Bag Pramuka",
            "fashion",
            "75000",
            40,
            "pcs",
            "active",
            28,
        ),
    ]
    for name, cat_slug, price, stock, unit, status, sold in produk:
        db.add(
            models.Product(
                store_id=toko.id,
                category_id=kategori[cat_slug].id,
                name=name,
                slug=unique_slug(db, models.Product, name),
                description=f"Produk sintetis: {name} (demo, bukan produk asli).",
                price=Decimal(price),
                stock=stock,
                unit=unit,
                images=DEMO_IMAGES.get(cat_slug),
                status=status,
                sold=sold,
            )
        )


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
        _seed_settings(db)
        _seed_categories(db)
        _seed_demo_data(db)
        db.commit()
    finally:
        db.close()
