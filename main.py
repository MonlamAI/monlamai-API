# main.py

from fastapi import FastAPI, Depends,Request
from fastapi.middleware.cors import CORSMiddleware
from v1.routes.translation import router as translationRoute
from v1.routes.tts import router as ttsRoute
from v1.routes.stt import router as sttRoute
from v1.routes.ocr import router as ocrRoute
from v1.routes.s3 import router as s3Route
import uvicorn
from v1.auth.auth_handler import verify_token 
import os 
import logging
from datetime import datetime
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
from v1.Config.Connection import prisma_connection

load_dotenv(override=True)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


description = """
## Monlam API helps you use our AI models. 🚀

"""
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])




app = FastAPI(
    title="Monlam API",
    description=description,
    summary="do not use without proper permissions",
    version="0.0.1",
    contact={
        "name": "monlam API service",
        "url": "https://monlam.ai",
        "email": "officials@monlam.com",
    })

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# database connection


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


@app.on_event("startup")
async def startup():
    await prisma_connection.connect()

@app.on_event("shutdown")
async def shutdown():
    await prisma_connection.disconnect()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log client IP, request method, and time."""
    client_ip = request.client.host
    method = request.method
    request_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    path = request.url.path
    
    logging.info(f"Client IP: {client_ip} | Time: {request_time} | Method: {method} | Path: {path}")

    # Call the next middleware or request handler
    
    response = await call_next(request)
    return response



@app.get("/")
def read_root():
    return {"message": "Welcome to API v1"}

# Include the v1 router with the prefix /api/v1
app.include_router(translationRoute, prefix="/api/v1/translation",dependencies=[Depends(verify_token)],tags=["translation"])
app.include_router(ocrRoute, prefix="/api/v1/ocr", dependencies=[Depends(verify_token)],tags=["ocr"])
app.include_router(sttRoute, prefix="/api/v1/stt", dependencies=[Depends(verify_token)],tags=["speech to text"])
app.include_router(ttsRoute, prefix="/api/v1/tts", dependencies=[Depends(verify_token)],tags=["text to speech"])
app.include_router(s3Route, prefix="/api/v1/upload", dependencies=[Depends(verify_token)],tags=["file upload"])




def get_port():
    """Retrieve the PORT from environment variables, defaulting to 8000 if not set."""
    port = os.getenv("PORT", 8000)  # Default to 8000 if PORT is not set
    try:
        return int(port)  # Ensure the port is an integer
    except ValueError:
        raise ValueError(f"Invalid PORT value: {port}. It must be an integer.")

if __name__ == "__main__":
    port = get_port()
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)