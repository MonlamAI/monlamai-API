from fastapi import APIRouter, HTTPException
from v1.utils.text_audio import tibetan_synthesizer
from pydantic import BaseModel
from v1.libs.upload_file_to_s3 import upload_file_to_s3
from v1.libs.base64_to_file_buffer import base64_to_file_buffer
import uuid
import base64
import time
router = APIRouter()
class Input(BaseModel):
    input: str
    

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
async def translate(request:Input):
       try:
        audio_data = await tibetan_synthesizer(
            request.input
        )
        base64=audio_data['audio']
        file_data = base64_to_file_buffer(base64)
        timestamp = int(time.time())
        file_name = f"{timestamp}_{uuid.uuid4()}-tts-audio.wav"
        file_url = await upload_file_to_s3(file_data, "audio/wav",file_name)
        return {
            "success": True,
            "output": file_url,
            "responseTime": audio_data['response_time'],
        }
    
       except Exception as e:
        raise HTTPException(status_code=500, detail=f"audio failed: {str(e)}")
