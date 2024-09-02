from fastapi import APIRouter, HTTPException
from v1.utils.translator import translator
from v1.utils.translator import translator_stream

from pydantic import BaseModel

router = APIRouter()

class Input(BaseModel):
    input: str
    target: str
    

@router.get("/")
def read_root():
    return {"message": "Welcome to API v1 translation"}

@router.get("/check")
async def check_translation():
       text='hi hello how are you',
       direction='bo'
       try:
        translated = await translator(
            text, direction
        )

        return {
            "success": True,
            "translation": translated['translation'],
            "responseTime": translated['responseTime'],
        }
    
       except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.post("/")
async def translate(request:Input):
       try:
        translated = await translator(
            request.input, request.target
        )

        return {
            "success": True,
            "translation": translated['translation'],
            "responseTime": translated['responseTime'],
        }
    
       except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.post("/stream")
async def stream_translate(request: Input):
    if not request.input or not request.target:
        raise HTTPException(status_code=400, detail="Missing input or target field.")

    try:
        translated =await translator_stream(request.input, request.target)
        return translated
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")