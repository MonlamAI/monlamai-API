from typing import Optional, Dict, Any, Callable
from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel, Field
from uuid import uuid4

from v1.utils.translator import (
    translator_llm, 
    translator_mt, 
    translator_stream_llm, 
    translator_stream_mt
)
from v1.utils.language_detect import detect_language
from v1.utils.utils import get_client_metadata
from v1.utils.get_userId_from_cookie import get_user_id_from_cookie
from v1.model.create_inference import create_translation
from v1.model.edit_inference import edit_inference
from v1.libs.chunk_text import chunk_tibetan_text
from v1.utils.mixPanel_track import track_user_input

import asyncio
import os
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address
from mixpanel import Mixpanel

# Load environment variables
load_dotenv()

# Configuration constants
MIXPANEL_TOKEN = os.getenv('MIXPANEL_TOKEN', '')
MAX_CONCURRENT_REQUESTS = 5
CHUNK_MAX_SIZE = 50
VERSION = "1.0.0"
DEFAULT_STREAM_PROVIDER = 'mt'

# Setup router and rate limiter
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()
mixpanel_client = Mixpanel(MIXPANEL_TOKEN)

class TranslationInput(BaseModel):
    """Model for translation input validation"""
    input: str = Field(..., min_length=1, description="Text to translate")
    target: str = Field(..., min_length=1, description="Target language code")

class TranslationResponse:
    """Helper class for creating consistent translation responses"""
    @staticmethod
    def create(
        success: bool = True, 
        translation: Optional[str] = None, 
        response_time: Optional[float] = None, 
        translation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a standardized translation response"""
        response = {"success": success}
        if translation:
            response["translation"] = translation
        if response_time:
            response["responseTime"] = response_time
        if translation_id:
            response["id"] = translation_id
        return response

def chunk_text(text: str, lang: str, max_chunk_size: int = CHUNK_MAX_SIZE) -> list:
    """
    Chunk text based on language-specific rules
    
    Args:
        text (str): Input text to chunk
        lang (str): Language of the text
        max_chunk_size (int): Maximum number of words per chunk
    
    Returns:
        list: Chunks of text
    """
    if lang == "bo":
        return chunk_tibetan_text(text, max_chunk_size)
    
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= max_chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

async def track_translation_event(
    user_id: str, 
    request: Request, 
    input_text: str, 
    output_text: str, 
    input_lang: str, 
    target_lang: str, 
    response_time: float, 
    model: str, 
    is_stream: bool = False
) -> None:
    """
    Track translation event in Mixpanel
    
    Args:
        user_id (str): User identifier
        request (Request): Client request object
        input_text (str): Original input text
        output_text (str): Translated text
        input_lang (str): Source language
        target_lang (str): Target language
        response_time (float): Translation response time
        model (str): Translation model used
        is_stream (bool): Whether streaming was used
    """
    client_ip, source_app, city, country = get_client_metadata(request)
    
    mixpanel_data = {
        "user_id": user_id,
        "type": 'Translation',
        "input": input_text,
        "output": output_text,
        "input_lang": input_lang,
        "output_lang": target_lang,
        "ip_address": client_ip,
        "city": city,
        "country": country,
        "response_time": response_time,
        "version": VERSION,
        "source_app": source_app,
        "model": model,
        "is_stream": is_stream
    }
    
    track_user_input(mixpanel_data, request)

@router.get("/")
async def check_translation(client_request: Request):
    """
    Health check endpoint for translation service
    
    Args:
        client_request (Request): Client request object
    
    Returns:
        dict: Translation check result
    """
    text = "hi hello how are you"
    direction = "bo"
    
    try:
        # Try getting translation from MT
        try:
            translated = await translator_mt(text, direction)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Mitra has issues: {str(e)}")
        
        # Try getting translation from LLM
        try:
            translation_result = await translator_llm(text, direction)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM has issues: {str(e)}")
        
        # Return combined result
        return TranslationResponse.create(
            translation=translated['translation'] + translation_result['translation'], 
            response_time=translated['responseTime'],
        )
    
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions
        raise http_exc
    
    except Exception as e:
        # Catch-all for any unexpected issues
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.post("/")
async def translate(request: TranslationInput, client_request: Request):
    try:
        user_id = await get_user_id_from_cookie(client_request)
        input_lang = detect_language(request.input) or ""
        
        # Chunk and translate text
        chunked_texts = chunk_text(request.input, input_lang)
        translated_text = ""
        
        for text_chunk in chunked_texts:
            translation_result = await translator_llm(text_chunk, request.target)
            translated_text += translation_result['translation']
        
        # Generate unique ID for this translation
        translation_id = str(uuid4())
        
        # Track and save translation event
        await track_translation_event(
            user_id=user_id,
            request=client_request,
            input_text=request.input,
            output_text=translated_text,
            input_lang=input_lang,
            target_lang=request.target,
            response_time=translation_result['responseTime'],
            model="melong",
            is_stream=False
        )
        
        # Save translation in background
        asyncio.create_task(create_translation({
            "id": translation_id,
            "input": request.input,
            "output": translated_text,
            "input_lang": input_lang,
            "output_lang": request.target,
            "response_time": translation_result['responseTime'],
            "user_id": user_id
        }))
        
        return TranslationResponse.create(
            translation=translated_text, 
            response_time=translation_result['responseTime'], 
            translation_id=translation_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.post("/stream")
async def stream_translate(request: TranslationInput, client_request: Request):
   
    user_id = await get_user_id_from_cookie(client_request)
    inference_id = str(uuid4())
    
    if not request.input or not request.target:
        raise HTTPException(status_code=400, detail="Missing input or target field.")

    try:
        async def on_complete(generated_text: str, response_time: float) -> None:
          
            if generated_text:
                input_lang = detect_language(request.input)
                await track_translation_event(
                    user_id=user_id,
                    request=client_request,
                    input_text=request.input,
                    output_text=generated_text,
                    input_lang=input_lang,
                    target_lang=request.target,
                    response_time=response_time,
                    model="melong",
                    is_stream=True
                )
                client_ip, source_app, city,country = get_client_metadata(client_request)

                asyncio.create_task(create_translation({
                    "id": inference_id,
                    "input": request.input, 
                    "output": generated_text,  
                    "input_lang": input_lang, 
                    "output_lang": request.target, 
                    "response_time": response_time,  
                    "user_id": user_id,
                    "ip_address": client_ip,
                    "version": "1.0.0",
                    "source_app": source_app,
                    "city": city,
                    "country": country,
                }))
        async def mt_on_complete(generated_text: str, response_time: float) -> None:
            if generated_text:
                input_lang = detect_language(request.input)
                await track_translation_event(
                    user_id=user_id,
                    request=client_request,
                    input_text=request.input,
                    output_text=generated_text,
                    input_lang=input_lang,
                    target_lang=request.target,
                    response_time=response_time,
                    model="matlad",
                    is_stream=True
                )
                client_ip, source_app, city,country = get_client_metadata(client_request)

                asyncio.create_task(create_translation({
                    "id": inference_id,
                    "input": request.input, 
                    "output": generated_text,  
                    "input_lang": input_lang, 
                    "output_lang": request.target, 
                    "response_time": response_time,  
                    "user_id": user_id,
                    "ip_address": client_ip,
                    "version": "1.0.0",
                    "source_app": source_app,
                    "city": city,
                    "country": country,
                }))

        provider_order = ["mt", "llm"] if DEFAULT_STREAM_PROVIDER == "mt" else ["llm", "mt"]

        async def run_provider(kind: str):
            if kind == "llm":
                return await translator_stream_llm(
                    request.input,
                    request.target,
                    inference_id,
                    on_complete=on_complete
                )
            else:
                return await translator_stream_mt(
                    request.input,
                    request.target,
                    inference_id,
                    on_complete=mt_on_complete
                )

        last_error = None
        for provider in provider_order:
            try:
                return await run_provider(provider)
            except Exception as e:
                last_error = e
                print(f"{provider.upper()} stream translation failed: {e}")
                continue
        if last_error:
            raise last_error
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")
    
@router.post("/mt")
async def translate_mt(request: TranslationInput, client_request: Request):
   
    try:
        user_id = await get_user_id_from_cookie(client_request)
        input_lang = detect_language(request.input) or ""
        
        # Chunk and translate text
        chunked_texts = chunk_text(request.input, input_lang)
        translated_text = ""
        
        for text_chunk in chunked_texts:
            translation_result = await translator_mt(text_chunk, request.target)
            translated_text += translation_result['translation']
        
        # Generate unique ID for this translation
        translation_id = str(uuid4())
        
        # Track and save translation event
        await track_translation_event(
            user_id=user_id,
            request=client_request,
            input_text=request.input,
            output_text=translated_text,
            input_lang=input_lang,
            target_lang=request.target,
            response_time=translation_result['responseTime'],
            model="matlad",
            is_stream=False
        )
        client_ip, source_app, city,country = get_client_metadata(client_request)
        # Save translation in background
        asyncio.create_task(create_translation({
            "id": translation_id+'-mitra',
            "input": request.input,
            "output": translated_text,
            "input_lang": input_lang,
            "output_lang": request.target,
            "response_time": translation_result['responseTime'],
            "user_id": user_id,
             "ip_address": client_ip,
             "version": "1.0.0",
             "source_app": source_app,
             "city": city,
            "country": country,
        }))
      
        return TranslationResponse.create(
            translation=translated_text, 
            response_time=translation_result['responseTime'], 
            translation_id=translation_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.post("/mt/stream")
async def stream_translate_mt(request: TranslationInput, client_request: Request):
 
    user_id = await get_user_id_from_cookie(client_request)
    inference_id = str(uuid4())
    
    if not request.input or not request.target:
        raise HTTPException(status_code=400, detail="Missing input or target field.")

    try:
        async def on_complete(generated_text: str, response_time: float) -> None:
            """
            Callback function for stream translation completion
            
            Args:
                generated_text (str): Full translated text
                response_time (float): Translation response time
            """
            if generated_text:
                input_lang = detect_language(request.input)
                await track_translation_event(
                    user_id=user_id,
                    request=client_request,
                    input_text=request.input,
                    output_text=generated_text,
                    input_lang=input_lang,
                    target_lang=request.target,
                    response_time=response_time,
                    model="matlad",
                    is_stream=True
                )
                client_ip, source_app, city,country = get_client_metadata(client_request)
                
                asyncio.create_task(create_translation({
                    "id": inference_id+'-mitra',
                    "input": request.input, 
                    "output": generated_text,  
                    "input_lang": input_lang, 
                    "output_lang": request.target, 
                    "response_time": response_time,  
                    "user_id": user_id,
                    "ip_address": client_ip,
                    "version": "1.0.0",
                    "source_app": source_app,
                    "city": city,
                    "country": country,
                }))
        
        # Await the streaming translation with the on_complete callback
        translated = await translator_stream_mt(
            request.input, 
            request.target,
            inference_id,
            on_complete=on_complete
        )
        
        return translated
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.put("/{translation_id}")
async def update_translation(
    translation_id: str,
    action: str = Query(..., description="Action to perform: 'edit', 'like', or 'dislike'"),
    edit_text: Optional[str] = None
):
    # Validate the action type
    if action == 'edit' and not edit_text:
        raise HTTPException(status_code=400, detail="Edit text must be provided for 'edit' action.")
    
    # Call the edit_inference function with the appropriate action
    updated_translation = await edit_inference('translation', translation_id, action, edit_text)

    if not updated_translation:
        raise HTTPException(status_code=404, detail="Translation not found")

    return {"message": f"Translation {action}d successfully", "data": updated_translation}