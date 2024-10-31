from fastapi import APIRouter, HTTPException,Request,Query,BackgroundTasks
from v1.utils.translator import translator
from v1.utils.translator import translator_stream
from typing import Optional
from pydantic import BaseModel
from v1.utils.language_detect import detect_language
from v1.model.create_inference import create_translation
from v1.utils.utils import get_client_metadata
from v1.utils.utils import get_user_id
import asyncio
from v1.model.edit_inference import edit_inference
from v1.utils.get_id_token import get_id_token
import queue
import uuid
from v1.libs.chunk_text import chunk_tibetan_text
from slowapi import Limiter
from slowapi.util import get_remote_address
from mixpanel import Mixpanel
import os
from dotenv import load_dotenv

load_dotenv()

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()
class Input(BaseModel):
    input: str
    target: str
    
# Limit to 5 concurrent requests
semaphore = asyncio.Semaphore(5)
MIXPANEL_TOKEN = os.getenv('MIXPANEL_TOKEN')
# Queue to hold pending requests
request_queue = queue.Queue()
mp = Mixpanel(MIXPANEL_TOKEN)


@router.get("/")
async def check_translation(client_request: Request):
       text="hi hello how are you"
       direction="bo"
       try:
            translated = await translator(text, direction)
            client_ip, source_app, city,country = get_client_metadata(client_request)
           
            return {
            "success": True,
            "translation": translated['translation'],
            "responseTime": translated['responseTime'],
            }
    
       except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@router.post("/proxy")
@limiter.exempt
async def proxy(request: Input):
    try:
        translated = await translator(request.input, request.target)
        # save translations
        return {
            "success": True,
            "translation": translated['translation'],
            "responseTime": translated['responseTime'],
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.post("/")

async def translate(request:Input, client_request: Request):
    token=get_id_token(client_request)
    user_id =await get_user_id(token)
    lang=detect_language(request.input)
    try:
        chunked_text= chunk_text(request.input,lang,50)
        translated_text=""
        for text in chunked_text:
           translated = await translator(text, request.target)
           translated_text+=translated['translation']
        # save translations
        generated_id=  str(uuid.uuid4())
        input_lang = detect_language(request.input) or ""
        client_ip, source_app, city,country = get_client_metadata(client_request)
        translation_data = {
                            "id":generated_id,
                            "input": request.input, 
                            "output": translated_text,  
                            "input_lang": input_lang, 
                            "output_lang": request.target, 
                            "response_time": translated['responseTime'],  
                            "ip_address": client_ip,
                            "version": "1.0.0",                        
                            "source_app": source_app,
                            "user_id": user_id,  
                            "city": city,
                            "country": country,
                            }
       
        asyncio.create_task(create_translation(translation_data))
        
        return {
            "success": True,
            "id":generated_id,
            "translation": translated_text,
            "responseTime": translated['responseTime'],
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@router.post("/stream")
async def stream_translate(request: Input, client_request: Request):
    token = get_id_token(client_request)
    user_id = await get_user_id(token)
    inference_id =  str(uuid.uuid4())
    if not request.input or not request.target:
        raise HTTPException(status_code=400, detail="Missing input or target field.")

    try:
        # Define the on_complete callback as an async function
        async def on_complete(generated_text, response_time):
            # Schedule the database save in the background
            if generated_text:
                 input_lang = detect_language(request.input)
                 client_ip, source_app, city, country = get_client_metadata(client_request)
                 translation_data = {
                            "id": inference_id,
                            "input": request.input, 
                            "output": generated_text,  
                            "input_lang": input_lang, 
                            "output_lang": request.target, 
                            "response_time": response_time,  
                            "ip_address": client_ip,
                            "version": "1.0.0",                        
                            "source_app": source_app,
                            "user_id": user_id,  
                            "city": city,
                            "country": country,
                            }
                 asyncio.create_task(create_translation(translation_data))
                 
        # Await the streaming translation with the on_complete callback
        translated = await translator_stream(
            request.input, 
            request.target,
            inference_id,  # Pass the inference ID
            on_complete=on_complete  # Pass the async function
        )
        
        return translated
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")



@router.put("/{translation_id}")
async def update_translation(
    translation_id: str,
    action: str = Query(..., description="Action to perform: 'edit', 'like', or 'dislike'"),
    edit_text: str = None  # Optional, only needed for the 'edit' action
):
    # Validate the action type
    if action == 'edit' and not edit_text:
        raise HTTPException(status_code=400, detail="Edit text must be provided for 'edit' action.")
    
    # Call the edit_inference function with the appropriate action
    updated_translation = await edit_inference('translation', translation_id, action, edit_text)

    if not updated_translation:
        raise HTTPException(status_code=404, detail="Translation not found")

    return {"message": f"Translation {action}d successfully", "data": updated_translation}


def chunk_text(text, lang, max=200):
    if lang == "bo":
        return chunk_tibetan_text(text, max)
    
    words = text.split(' ')
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= max:
            chunks.append(' '.join(current_chunk))
            current_chunk = []

    # Add any remaining words as the last chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks
