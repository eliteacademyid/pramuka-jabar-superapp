from tests.conftest import admin_token, headers, login, register

import app.routers.ai as ai_mod


async def _fake_gemini(system_prompt: str, user_message: str) -> str:
    return "Halo! Ada yang bisa saya bantu seputar marketplace Pramuka Jabar?"


def test_ai_chat_requires_auth(client):
    r = client.post("/api/ai/chat", json={"message": "halo"})
    assert r.status_code in (401, 403)


def test_ai_chat_empty_message(client):
    register(client, "ai_user1")
    token = login(client, "ai_user1")
    r = client.post(
        "/api/ai/chat",
        json={"message": ""},
        headers=headers(token),
    )
    assert r.status_code == 422


def test_ai_chat_message_too_long(client):
    register(client, "ai_user2")
    token = login(client, "ai_user2")
    r = client.post(
        "/api/ai/chat",
        json={"message": "x" * 2001},
        headers=headers(token),
    )
    assert r.status_code == 422


def test_ai_chat_missing_key(client, monkeypatch):
    register(client, "ai_user3")
    token = login(client, "ai_user3")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    r = client.post(
        "/api/ai/chat",
        json={"message": "cara top up?"},
        headers=headers(token),
    )
    assert r.status_code == 503
    assert "belum dikonfigurasi" in r.json()["detail"]


def test_ai_chat_success(client, monkeypatch):
    register(client, "ai_user4")
    token = login(client, "ai_user4")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setattr(ai_mod, "_call_gemini", _fake_gemini)
    r = client.post(
        "/api/ai/chat",
        json={"message": "cara buka toko?"},
        headers=headers(token),
    )
    assert r.status_code == 200
    assert "marketplace" in r.json()["reply"]
