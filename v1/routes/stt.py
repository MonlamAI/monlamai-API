from fastapi import APIRouter, HTTPException,Request,Query
from v1.utils.speech_recognition import speech_to_text_tibetan,speech_to_text_english
from v1.libs.get_buffer import get_buffer
from pydantic import BaseModel
from v1.utils.utils import get_user_id
from typing import Optional
from v1.utils.utils import get_client_metadata
from v1.model.create_inference import create_speech_to_text
from v1.model.edit_inference import edit_inference
from v1.utils.get_id_token import get_id_token
router = APIRouter()

class Input(BaseModel):
    input: str
    lang: Optional[str] = None

@router.get("/")

async def check_speech_to_text():
       audio_url ="https://s3.ap-south-1.amazonaws.com/monlam.ai.website/STT/input/1719051360666-undefined"
       audio=await get_buffer(audio_url)
       try:   
         text_data =await speech_to_text_tibetan(audio)
         return {
            "success": True,
            "audio": text_data['text'],
            "responseTime": text_data['response_time'],
            }
    
       except Exception as e:
        raise HTTPException(status_code=500, detail=f"audio failed: {str(e)}")

@router.post("/")
async def speech_to_text_func(request:Input, client_request: Request):
       token = get_id_token(client_request)
       user_id =await get_user_id(token)
       try:
        audio_url=request.input
        lang=request.lang
        audio=await get_buffer(audio_url)
        client_ip, source_app,city,country = get_client_metadata(client_request)
        text_data, response_time = await transcribe_audio(audio, lang)
        stt_data = {
        "input": request.input,
        "output": text_data,
        "response_time": response_time,
        "ip_address": client_ip,
        "version": "wav2vec2_run10",
        "source_app": source_app,
        "user_id": user_id,
        "city": city,
        "country": country,
        }
        data= await create_speech_to_text(stt_data)
        return {
            "success": True,
            "id":data.id,
            "output": text_data,
            "responseTime": response_time,
        }
    
       except Exception as e:
        raise HTTPException(status_code=500, detail=f"audio failed: {str(e)}")



@router.put("/{id}")
async def update_speechtotext(id: int, action: str = Query(..., description="Action to perform: 'edit', 'like', or 'dislike'"), edit_text: str = None):
    # Validate the action type
    if action == 'edit' and not edit_text:
        raise HTTPException(status_code=400, detail="Edit text must be provided for 'edit' action.")

    # Call the edit_inference function to update the record in speechtotexts table
    updated_record = await edit_inference('speechtotexts', id, action, edit_text)

    if not updated_record:
        raise HTTPException(status_code=404, detail="Record not found")

    return {"message": f"Record {action}d successfully", "data": updated_record}




    

async def transcribe_audio(audio, lang):
    if lang and lang != 'bo':
        # Call Whisper if a specific language is provided and it's not 'bo'
        text_data =await speech_to_text_english(audio)
        response_time = round(text_data['response_time'] * 1000, 4)
    else:
        # Call general speech-to-text function for language 'bo'
        text_data = await speech_to_text_tibetan(audio)
        response_time = round(text_data['response_time'] * 1000, 4)
       
    text_data = text_data['text']
    return text_data, response_time