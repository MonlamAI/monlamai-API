from fastapi import APIRouter, HTTPException,Request
from v1.utils.speech_recognition import speech_to_text
from v1.libs.get_buffer import get_buffer
from v1.utils.whisper_stt import whisper_stt
from pydantic import BaseModel
from v1.utils.utils import get_user_id
from db import get_db
from typing import Optional
from v1.utils.utils import get_client_metadata
from v1.model.create_inference import create_speech_to_text
router = APIRouter()

class Input(BaseModel):
    input: str
    lang: Optional[str] = None
    id_token:Optional[str] = None

@router.get("/")

async def check_speech_to_text():
       audio_url ="https://s3.ap-south-1.amazonaws.com/monlam.ai.website/STT/input/1719051360666-undefined"
       audio=await get_buffer(audio_url)
       try:   
         text_data =await speech_to_text(audio)
         return {
            "success": True,
            "audio": text_data['text'],
            "responseTime": text_data['response_time'],
            }
    
       except Exception as e:
        raise HTTPException(status_code=500, detail=f"audio failed: {str(e)}")

@router.post("/")
async def speech_to_text_func(request:Input, client_request: Request):
       token = request.id_token
       user_id = get_user_id(token)
       try:
        audio_url=request.input
        lang=request.lang
        audio=await get_buffer(audio_url)
        client_ip, source_app = get_client_metadata(client_request)
        text_data, response_time = await transcribe_audio(audio, lang)
        db = next(get_db())
        save_stt_data(db, request.input, text_data, response_time, client_ip, source_app, user_id)

        return {
            "success": True,
            "output": text_data,
            "responseTime": response_time,
        }
    
       except Exception as e:
        raise HTTPException(status_code=500, detail=f"audio failed: {str(e)}")


def save_stt_data(db, input, output, response_time, client_ip, source_app, user_id):
    
     stt_data = {
        "input": input,
        "output": output,
        "response_time": response_time,
        "ip_address": client_ip,
        "version": None,
        "source_app": source_app,
        "user_id": user_id,
     }
     create_speech_to_text(db, stt_data)

async def transcribe_audio(audio, lang):
    print(audio,lang)
    if lang and lang != 'bo':
        # Call Whisper if a specific language is provided and it's not 'bo'
        text_data = whisper_stt(audio)
        response_time = "whisper"
    else:
        # Call general speech-to-text function for language 'bo'
        text_data = await speech_to_text(audio)
        response_time = round(text_data['response_time'] * 1000, 4)
       
        text_data = text_data['text']
    return text_data, response_time