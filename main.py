# main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from v1.translation import router as translationRoute
from v1.tts import router as ttsRoute
from v1.stt import router as sttRoute
from v1.ocr import router as ocrRoute
import uvicorn
from v1.auth.auth_handler import verify_token 
from dotenv import load_dotenv

load_dotenv(override=True)

description = """
## Monlam API helps you use our AI models. 🚀

"""

app = FastAPI(
    title="Monlam API",
    description=description,
    summary="do not use without proper permissions",
    version="0.0.1",
    # terms_of_service="http://example.com/terms/",
    contact={
        "name": "monlam API service",
        "url": "https://monlam.ai",
        "email": "officials@monlam.com",
    })

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def read_root():
    return {"message": "Welcome to API v1"}

# Include the v1 router with the prefix /api/v1
app.include_router(translationRoute, prefix="/api/v1/translation",dependencies=[Depends(verify_token)],tags=["translation"])
app.include_router(ocrRoute, prefix="/api/v1/ocr", dependencies=[Depends(verify_token)],tags=["ocr"])
app.include_router(sttRoute, prefix="/api/v1/stt", dependencies=[Depends(verify_token)],tags=["speech to text"])
app.include_router(ttsRoute, prefix="/api/v1/tts", dependencies=[Depends(verify_token)],tags=["text to speech"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=1000, reload=True)