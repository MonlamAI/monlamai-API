import os
import json
import httpx
from v1.utils.translator import headers
import asyncio
import aiohttp


async def speech_to_text_tibetan(audio:str) -> dict:
    """Convert speech to text using the STT model."""
    
    MODEL_AUTH = os.getenv('MODEL_AUTH')
    api_url = os.getenv('STT_MODEL_URL')
    response_time = 0
   
    headers = {
        "Content-Type": "audio/flac",
        "Authorization": f"Bearer {MODEL_AUTH}",
        "Access-Control-Allow-Origin": "*",
    }
    
    
    try:
        start_time = asyncio.get_event_loop().time()  # Record start time
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, headers=headers, content=audio)
            data = response.json()
            end_time = asyncio.get_event_loop().time()  # Record end time
            response_time = end_time - start_time  # Calculate response time
            return {"text":data['text'],"response_time":response_time}

    except httpx.HTTPStatusError as http_error:
        # Handle HTTP errors
        return {"error": "error in speech to text http", "details": str(http_error)}
    except Exception as e:
        # Handle other possible errors

        return {"error": "error in speech to text", "details": str(e)}


async def speech_to_text_english(audio:str) -> dict:
    
    """Convert speech to text using the STT model."""
    
    MODEL_AUTH = os.getenv('MODEL_AUTH')
    api_url = os.getenv('STT_MODEL_URL_ENGLISH')
    response_time = 0
   
    headers = {
        "Content-Type": "audio/flac",
        "Authorization": f"Bearer {MODEL_AUTH}",
        "Accept" : "application/json",
    }
    
    try:
        start_time = asyncio.get_event_loop().time()  # Record start time
        print(audio)
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, headers=headers, content=audio)
            data = response.json()
            end_time = asyncio.get_event_loop().time()  # Record end time
            response_time = end_time - start_time  # Calculate response time
            return {"text":data['text'],"response_time":response_time}

    except httpx.HTTPStatusError as http_error:
        # Handle HTTP errors
        return {"error": "error in speech to text http", "details": str(http_error)}
    except Exception as e:
        # Handle other possible errors

        return {"error": "error in speech to text", "details": str(e)}
