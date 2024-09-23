from fastapi import APIRouter, HTTPException,Request,Query
from v1.utils.translator import translator
from v1.utils.translator import translator_stream
from typing import Optional
from pydantic import BaseModel
from v1.utils.language_detect import detect_language
from v1.auth.token_verify import verify
from v1.model.create_inference import create_translation
from v1.utils.utils import get_client_metadata
from v1.utils.utils import get_user_id
import asyncio
from v1.model.edit_inference import edit_inference
from v1.utils.get_id_token import get_id_token
import json
router = APIRouter()

class Input(BaseModel):
    input: str
    target: str
    inference_id: Optional[str] = None
    


@router.get("/")
async def check_translation():
       text="hi hello how are you"
       direction="bo"
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
    token=get_id_token(client_request)
    user_id =await get_user_id(token)
    inference_id = request.inference_id
    try:
        translated = await translator(request.input, request.target)
        # save translations
        
        input_lang = detect_language(request.input) or ""
        client_ip, source_app, city,country = get_client_metadata(client_request)
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
                            "city": city,
                            "country": country,
                            }
        if inference_id:
            translation_data["id"] = inference_id
        asyncio.create_task(create_translation(translation_data))
        
        return {
            "success": True,
            "translation": translated['translation'],
            "responseTime": translated['responseTime'],
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@router.post("/stream")
async def stream_translate(request: Input, client_request: Request):
    token = get_id_token(client_request)
    user_id = await get_user_id(token)
    inference_id = request.inference_id
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
                 if inference_id:
                           translation_data["id"] = inference_id
                 asyncio.create_task(create_translation(translation_data))
                 
        # Await the streaming translation with the on_complete callback
        translated = await translator_stream(
           request.input, 
            request.target,
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



