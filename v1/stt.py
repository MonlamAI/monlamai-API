from fastapi import APIRouter, HTTPException
from v1.utils.speech_recognition import speech_to_text
from v1.libs.url_to_buffer import get_buffer

from pydantic import BaseModel
import httpx

router = APIRouter()

class Input(BaseModel):
    input: str


@router.get("/")
async def check_stt():
       audio_url ="https://s3.ap-south-1.amazonaws.com/monlam.ai.website/STT/input/1719051360666-undefined"
       try:
        text_data = await speech_to_text(
           await get_buffer(audio_url)
        )
        return {
            "success": True,
            "audio": text_data['text'],
            "responseTime": text_data['response_time'],
        }
    
       except Exception as e:
        raise HTTPException(status_code=500, detail=f"audio failed: {str(e)}")

@router.post("/")
async def translate(request:Input):
       try:
        audio_url=request.input
        audio=await get_buffer(audio_url)
        text_data = await speech_to_text(audio)
        return {
            "success": True,
            "output": text_data['text'],
            "responseTime": text_data['response_time'],
        }
    
       except Exception as e:
        raise HTTPException(status_code=500, detail=f"audio failed: {str(e)}")
