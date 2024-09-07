from fastapi import APIRouter, HTTPException,Request
from v1.utils.translator import translator
from v1.utils.translator import translator_stream
from typing import Optional
from pydantic import BaseModel
from v1.utils.language_detect import detect_language
from v1.auth.token_verify import verify
from db import get_db
from v1.model.create_inference import create_translation
from v1.utils.utils import get_client_metadata
from v1.utils.utils import get_user_id

router = APIRouter()

class Input(BaseModel):
    input: str
    target: str
    id_token: Optional[str] = None
    

@router.get("/")
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

async def translate(request:Input, client_request: Request):
    token=request.id_token
    user_id = get_user_id(token)
    try:
        translated = await translator(request.input, request.target)
        # save translations
        db=next(get_db())
        
        input_lang=detect_language(request.input)
        client_ip, source_app = get_client_metadata(client_request)
        translation_data = {
                            "input": request.input, 
                            "output": translated['translation'],  
                            "input_lang": input_lang, 
                            "output_lang": request.target, 
                            "response_time": translated['responseTime'],  
                            "ip_address": client_ip,
                            "version": "1.0.0",                        
                            "source_app": source_app,
                            "user_id": user_id,  
                            }
        create_translation(db,translation_data) 
        
        return {
            "success": True,
            "translation": translated['translation'],
            "responseTime": translated['responseTime'],
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.post("/stream")
async def stream_translate(request: Input, client_request: Request):
    token=request.id_token
    user_id = get_user_id(token)
       
    if not request.input or not request.target:
        raise HTTPException(status_code=400, detail="Missing input or target field.")

    try:
        translated =await translator_stream(request.input, request.target,on_complete=lambda generated_text, response_time: save_translation_to_db(
                generated_text, 
                request.input, 
                request.target, 
                client_request, 
                user_id,
                response_time
            ))
                
        return translated
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")
    
    
async def save_translation_to_db(generated_text: str, text: str, direction: str, request: Request, user_id: int, response_time: float):
    # Only save if generated_text exists
    if generated_text:
        db = next(get_db())
        input_lang = detect_language(text)
        client_ip, source_app = get_client_metadata(request)
        
        translation_data = {
            "input": text,
            "output": generated_text,
            "input_lang": input_lang,
            "output_lang": direction,
            "response_time": response_time,  # Now we pass the calculated response time
            "ip_address": client_ip,
            "version": "1.0.0",
            "source_app": source_app,
            "user_id": user_id,
        }

        create_translation(db, translation_data)
