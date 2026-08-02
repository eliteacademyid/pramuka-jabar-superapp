from conftest import headers, login, register

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"


def test_register_success(client):
    r = register(client, "new_member")
    assert r.status_code == 201
    body = r.json()
    assert body["username"] == "new_member"
    assert body["role"] == "member"


def test_register_duplicate_username(client):
    assert register(client, "dup_user").status_code == 201
    assert register(client, "dup_user").status_code == 409


def test_register_invalid_account_type(client):
    r = register(client, "bad_type", account_type="alien")
    assert r.status_code == 422


def test_register_short_password(client):
    r = register(client, "shortpass", password="abc")
    assert r.status_code == 422


def test_login_success_and_me(client):
    register(client, "login_user")
    token = login(client, "login_user")
    r = client.get("/api/auth/me", headers=headers(token))
    assert r.status_code == 200
    body = r.json()
    assert body["user"]["username"] == "login_user"
    assert body["wallet"] is not None
    assert body["store"] is None


def test_login_wrong_password(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "salah"})
    assert r.status_code == 401


def test_login_inactive_user(client):
    register(client, "inactive_user")
    token = login(client, ADMIN_USER, ADMIN_PASS)
    users = client.get("/api/admin/users", headers=headers(token)).json()
    target = next(u for u in users if u["username"] == "inactive_user")
    client.put(f"/api/admin/users/{target['id']}", json={"is_active": False}, headers=headers(token))
    assert client.post("/api/auth/login", json={"username": "inactive_user", "password": "password123"}).status_code == 401


def test_me_requires_token(client):
    assert client.get("/api/auth/me").status_code in (401, 403)


def test_theme_default_and_update(client):
    register(client, "theme_user")
    token = login(client, "theme_user")
    r = client.get("/api/me/theme", headers=headers(token))
    assert r.status_code == 200
    assert r.json()["theme"] == "default"

    r = client.put("/api/me/theme", json={"theme": "dark"}, headers=headers(token))
    assert r.status_code == 200
    assert r.json()["theme"] == "dark"

    r = client.put("/api/me/theme", json={"theme": "blue"}, headers=headers(token))
    assert r.status_code == 200
    assert r.json()["theme"] == "blue"

    r = client.put("/api/me/theme", json={"theme": "neon"}, headers=headers(token))
    assert r.status_code == 422

    r = client.put("/api/me/theme", json={"theme": "default"}, headers=headers(token))
    assert r.json()["theme"] == "default"

    r = client.get("/api/auth/me", headers=headers(token))
    assert r.json()["user"]["theme"] == "default"

    assert client.get("/api/me/theme").status_code in (401, 403)


def test_update_profile(client):
    register(client, "profile_user")
    token = login(client, "profile_user")
    r = client.put(
        "/api/me",
        json={"nama_lengkap": "Nama Baru", "email": "baru@example.test"},
        headers=headers(token),
    )
    assert r.status_code == 200
    assert r.json()["nama_lengkap"] == "Nama Baru"
    me = client.get("/api/auth/me", headers=headers(token)).json()
    assert me["user"]["email"] == "baru@example.test"


def test_admin_seed_login(client):
    token = login(client, ADMIN_USER, ADMIN_PASS)
    assert token
