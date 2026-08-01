import os

os.environ["DATABASE_URL"] = "sqlite:///./test_javascout.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import auth, models
from app.database import Base, get_db
from app.main import app
from app.seed import (
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_USERNAME,
    _seed_categories,
    _seed_demo_data,
    _seed_settings,
)


def _seed_all(db):
    db.add(
        models.User(
            username=DEFAULT_ADMIN_USERNAME,
            hashed_password=auth.hash_password(DEFAULT_ADMIN_PASSWORD),
            nama_lengkap="Administrator",
            role="admin",
            is_active=True,
        )
    )
    _seed_settings(db)
    _seed_categories(db)
    _seed_demo_data(db)
    db.commit()


@pytest.fixture()
def client(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    _seed_all(db)
    db.close()

    def override_get_db():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


# ---------- helpers ----------

def register(client, username="buyer_test", password="password123", **kw):
    payload = {
        "username": username,
        "password": password,
        "nama_lengkap": kw.pop("nama_lengkap", "Pembeli Test"),
        "account_type": kw.pop("account_type", "umum"),
    }
    payload.update(kw)
    return client.post("/api/auth/register", json=payload)


def login(client, username, password="password123"):
    r = client.post("/api/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def headers(token):
    return {"Authorization": f"Bearer {token}"}


def admin_token(client):
    return login(client, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)


def seller_token(client):
    return login(client, "member_budi")


def topup(client, token, amount=500000):
    r = client.post("/api/wallet/topup", json={"amount": amount}, headers=headers(token))
    assert r.status_code == 200, r.text
    return r.json()


def add_address(client, token, city="Bandung", province="Jawa Barat"):
    payload = {
        "label": "rumah",
        "address_line": "Jl. Test No. 1",
        "city": city,
        "province": province,
        "is_primary": True,
    }
    r = client.post("/api/me/addresses", json=payload, headers=headers(token))
    assert r.status_code == 201, r.text
    return r.json()


def add_cart(client, token, product_id, qty=1):
    r = client.post(
        "/api/cart/items", json={"product_id": product_id, "qty": qty}, headers=headers(token)
    )
    assert r.status_code == 201, r.text
    return r.json()


def checkout(client, token, address_id):
    r = client.post(
        "/api/cart/checkout", json={"address_id": address_id}, headers=headers(token)
    )
    assert r.status_code == 200, r.text
    return r.json()["orders"]


def demo_product(client):
    data = client.get("/api/products", params={"size": 1}).json()
    return data["items"][0]


def pay_order(client, token, code):
    return client.post(f"/api/orders/{code}/pay", headers=headers(token))


def confirm_order(client, token, order_id):
    return client.post(f"/api/seller/orders/{order_id}/confirm", headers=headers(token))


def ship_order(client, token, order_id):
    return client.post(
        f"/api/seller/orders/{order_id}/ship",
        json={"tracking_number": "TRK-TEST-1"},
        headers=headers(token),
    )


def confirm_receipt(client, token, code):
    return client.post(f"/api/orders/{code}/confirm-receipt", headers=headers(token))


def complete_purchase(client, buyer_token, product_id, qty=1, city="Bandung"):
    topup(client, buyer_token)
    add_address(client, buyer_token, city=city)
    add_cart(client, buyer_token, product_id, qty)
    code = checkout(client, buyer_token, 1)[0]
    r = pay_order(client, buyer_token, code)
    assert r.status_code == 200, r.text
    order = r.json()
    st = seller_token(client)
    assert confirm_order(client, st, order["id"]).status_code == 200
    assert ship_order(client, st, order["id"]).status_code == 200
    assert confirm_receipt(client, buyer_token, code).status_code == 200
    return code
