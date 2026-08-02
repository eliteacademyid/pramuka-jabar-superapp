from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from groq import Groq

from app.config import GROQ_API_KEY
from app.deps import get_current_user
from app import models

router = APIRouter()

# Initialize Groq API
client = None
if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)

class ChatRequest(BaseModel):
    message: str

SYSTEM_PROMPT = """
Kamu adalah "Tanya AI", asisten virtual pintar dan ramah yang dibuat khusus untuk aplikasi E-Pelatihan Pramuka Jawa Barat.
Tugas utamamu adalah membantu anggota Pramuka Jabar, admin, atau pelatih dengan menjawab pertanyaan seputar kepramukaan, 
panduan penggunaan aplikasi, atau materi pelatihan.

Aturan sifat dan gaya bahasa:
1. Selalu bersikap sopan, ramah, dan solutif.
2. Gunakan sapaan khas Pramuka seperti "Kak" (Kakak) kepada pengguna.
3. Jawab dengan bahasa Indonesia yang baik, asyik, dan mudah dipahami.
4. Jika tidak tahu jawabannya, arahkan mereka untuk bertanya langsung ke pelatih atau admin Kwarcab.
5. Jawab secara ringkas dan informatif.
"""

@router.post("/chat")
def chat_with_ai(request: ChatRequest, current_user: models.User = Depends(get_current_user)):
    if not GROQ_API_KEY or GROQ_API_KEY == "YOUR_GROQ_API_KEY_HERE":
        raise HTTPException(
            status_code=500, 
            detail="API Key Groq belum diatur oleh sistem. Silakan hubungi admin."
        )

    try:
        # Use llama-3.1-8b-instant for fast and reliable responses
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.message}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=1024
        )
        
        reply = chat_completion.choices[0].message.content
        return {"reply": reply}

    except Exception as e:
        print(f"Groq API Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Terjadi kesalahan saat memproses permintaan AI: {str(e)}"
        )
