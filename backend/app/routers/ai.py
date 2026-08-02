import os

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app import models, schemas
from app.deps import get_current_user

router = APIRouter(prefix="/ai", tags=["ai"])

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

SYSTEM_PROMPT = """Kamu adalah "Bantuan AI" dari SuperApps-JavaScout, superapp
marketplace UMKM dan toko anggota Pramuka Jawa Barat. Tugasmu membantu
pengguna aplikasi ini: cara berbelanja di katalog, keranjang & checkout,
top-up dan wallet dengan escrow (dana baru dilepas saat pesanan diterima),
status pesanan & konfirmasi penerimaan, pencairan dana penjual, membuka toko,
chat pembeli-penjual, mengajukan perselisihan/tiket, ganti tema (default,
gelap, biru cerah), dan fitur lain di aplikasi ini.
Jawablah singkat dan jelas dalam Bahasa Indonesia, maksimal 3-4 kalimat,
ramah, dan sesuai fakta aplikasi. Jika ditanya di luar konteks aplikasi ini,
arahkan kembali ke topik aplikasi secara sopan."""


async def _call_gemini(system_prompt: str, user_message: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bantuan AI belum dikonfigurasi oleh pengelola aplikasi",
        )
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent"
    )
    body = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_message}]}],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 700,
        },
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, params={"key": api_key}, json=body)
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Layanan AI sedang tidak tersedia, coba lagi nanti",
        )
    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Layanan AI mengembalikan kesalahan, coba lagi nanti",
        )
    try:
        reply = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Bantuan AI gagal memahami pertanyaan, coba lagi",
        )
    if not reply:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Bantuan AI tidak memberikan jawaban, coba lagi",
        )
    return reply


@router.post("/chat", response_model=schemas.AiChatOut)
async def ai_chat(
    payload: schemas.AiChatRequest,
    current_user: models.User = Depends(get_current_user),
):
    user_context = (
        f"Pengguna: {current_user.nama_lengkap} (username {current_user.username}, "
        f"peran {current_user.role}). "
        f"Pertanyaan: {payload.message.strip()}"
    )
    reply = await _call_gemini(SYSTEM_PROMPT, user_context)
    return {"reply": reply}
