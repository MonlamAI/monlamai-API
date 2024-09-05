from fastapi import APIRouter, HTTPException,Request
from v1.utils.text_audio import tibetan_synthesizer
from pydantic import BaseModel
from v1.libs.upload_file_to_s3 import upload_file_to_s3
from v1.libs.base64_to_file_buffer import base64_to_file_buffer
from v1.model.create_inference import create_text_to_speech
import uuid
from db import get_db
import time
from v1.utils.utils import get_client_metadata
from typing import Optional
from v1.utils.utils import get_user_id

router = APIRouter()
class Input(BaseModel):
    input: str
    id_token:Optional[str] = None

 

@router.get("/")
async def check_translation():
       text="ངའི་མིང་ལ་ཀུན་བཟང་རེད་།" 
       try:
        audio_data = await tibetan_synthesizer(
            text
        )

        return {
            "success": True,
            "audio": audio_data['audio'],
            "responseTime": audio_data['response_time'],
        }
    
       except Exception as e:
        raise HTTPException(status_code=500, detail=f"audio failed: {str(e)}")

@router.post("/")
async def text_to_speech(request: Input, client_request: Request):
    token = request.id_token
    user_id = get_user_id(token)

    try:
        # Generate audio data from text input
        audio_data = await tibetan_synthesizer(request.input)
        base64_audio = audio_data['audio']
        file_url = await handle_audio_file(base64_audio)

        # Get client IP and source application metadata
        client_ip, source_app = get_client_metadata(client_request)

        # Save the TTS data to the database
        db = next(get_db())
        response_time = round(audio_data['response_time'] * 1000, 4)
        save_tts_data(db, request.input, file_url, response_time, client_ip, source_app, user_id)

        # Return the result
        return {
            "success": True,
            "output": file_url,
            "responseTime": response_time,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio failed: {str(e)}")


async def handle_audio_file(base64_audio):
    file_data = base64_to_file_buffer(base64_audio)
    timestamp = int(time.time())
    file_name = f"{timestamp}_{uuid.uuid4()}-tts-audio.wav"
    file_url = await upload_file_to_s3(file_data, "audio/wav", file_name)
    return file_url


def save_tts_data(db, input_text, file_url, response_time, client_ip, source_app, user_id):
    tts_data = {
        "input": input_text,
        "output": file_url,
        "response_time": response_time,
        "ip_address": client_ip,
        "version": None,
        "source_app": source_app,
        "user_id": user_id,
    }
    create_text_to_speech(db, tts_data)