
import os
import httpx
import json
import asyncio
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from v1.utils.get_translation_from_file import get_translation_from_file,count_words
from db import get_db
from fastapi import Request
from v1.model.create_inference import create_translation
from v1.utils.language_detect import detect_language
from v1.utils.utils import get_client_metadata

import time


load_dotenv()
MODEL_AUTH = os.getenv('MODEL_AUTH')
MT_MODEL_URL = os.getenv('MT_MODEL_URL')
headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MODEL_AUTH}",
        "Access-Control-Allow-Origin": "*",
    }



async def translator(text: str, direction: str ):
    url = MT_MODEL_URL
    received_data = ""
    response_time = 0
    API_ERROR_MESSAGE = "error"
    word_count = count_words(text)
    
   
    if word_count <= 3:
        translation = get_translation_from_file(text,direction)
        if translation:
           return {"translation": translation, "responseTime": response_time}
    
    text_data = f"<2{direction}>{text}"
    
    try:
        start_time = time.time()  # Record start time
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={
                    "inputs": text_data,
                    "parameters": {
                        "max_new_tokens": 256,
                    },
                },
                headers=headers,
            )
        if response.status_code != 200:
            raise Exception(API_ERROR_MESSAGE)
        
        response_data = response.json()
        response_time = round((time.time() - start_time) * 1000, 4)
        received_data = response_data[0].get('generated_text', '')
    
    except Exception as e:
        raise Exception(API_ERROR_MESSAGE) from e
    
    
    translation = received_data
   
    return {"translation": translation, "responseTime": response_time}


async def translator_stream(text: str, direction: str, on_complete=None):
    # Retrieve environment variables
    text_data = f"<2{direction}>{text}"
    start_time = time.time()
    url = f"{MT_MODEL_URL}/generate_stream"
     # Retrieve the Origin and Referer headers

    word_count = count_words(text)
    
    # If the text has two or fewer words, try to get the translation from the file
    if word_count <= 2:
        translation = get_translation_from_file(text, direction)
        if translation:  # Only stream if a translation is found
            async def short_event_stream():
                yield f"data: {json.dumps({'generated_text': translation})}\n\n"
                if on_complete:
                    await on_complete(translation, 0)
            return StreamingResponse(short_event_stream(), media_type="text/event-stream")

    # Define the event stream generator
    async def event_stream():
        db=next(get_db())
        try:
            body = {
                "inputs": text_data,
                "parameters": {"max_new_tokens": 256},
            }

            async with httpx.AsyncClient() as client:
                async with client.stream("POST", url, json=body, headers=headers) as response:
                    async for chunk in response.aiter_bytes():
                        # Process each chunk of data
                        data = chunk.decode('utf-8').strip()
                        if not data:
                            continue

                        for line in data.split('\n'):
                            if line.startswith("data:"):
                                json_data = line[len("data:"):].strip()
                                if not json_data:
                                    continue

                                parsed_data = json.loads(json_data)
                                text_value = parsed_data.get("token", {}).get("text")
                                generated_text = parsed_data.get("generated_text")
                               
                                if text_value:
                                    yield f"data: {json.dumps({'text': text_value})}\n\n"

                                # Yield the generated text as an SSE event and end the stream
                                if generated_text:
                                    yield f"data: {json.dumps({'generated_text': generated_text})}\n\n"
                                    return
        except Exception as e:
            yield f"event: error\ndata: Stream error: {str(e)}\n\n"
        
        finally:
            end_time = time.time()  # Capture the end time
            response_time = round((end_time - start_time) * 1000, 4)
            if on_complete:
                await on_complete(generated_text, response_time)

    return StreamingResponse(event_stream(), media_type="text/event-stream")

 