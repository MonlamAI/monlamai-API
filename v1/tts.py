from fastapi import APIRouter, HTTPException
from v1.utils.text_audio import tibetan_synthesizer
from pydantic import BaseModel

router = APIRouter()

class Input(BaseModel):
    input: str
    

@router.get("/")
def read_root():
    return {"message": "Welcome to API v1 text to Speech"}

@router.get("/check")
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

        return {
            "success": True,
            "audio": audio_data['audio'],
            "responseTime": audio_data['response_time'],
        }
    
       except Exception as e:
        raise HTTPException(status_code=500, detail=f"audio failed: {str(e)}")
