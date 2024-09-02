
import os
import httpx
import json
import asyncio
import aiohttp
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, HTTPException 
from dotenv import load_dotenv

load_dotenv()

MODEL_AUTH = os.getenv('MODEL_AUTH')
MT_MODEL_URL = os.getenv('MT_MODEL_URL')

headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MODEL_AUTH}",
        "Access-Control-Allow-Origin": "*",
    }

async def translator(text: str, direction: str):
    url = MT_MODEL_URL
    text = f"<2{direction}>{text}"
    received_data = ""
    response_time = 0
    API_ERROR_MESSAGE = "error"
    
    try:
        start_time = asyncio.get_event_loop().time()  # Record start time
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={
                    "inputs": text,
                    "parameters": {
                        "max_new_tokens": 256,
                    },
                },
                headers=headers,
            )
        if response.status_code != 200:
            raise Exception(API_ERROR_MESSAGE)
        
        response_data = response.json()
        end_time = asyncio.get_event_loop().time()  # Record end time
        response_time = end_time - start_time  # Calculate response time
        received_data = response_data[0].get('generated_text', '')
    
    except Exception as e:
        raise Exception(API_ERROR_MESSAGE) from e

    translation = received_data
    return {"translation": translation, "responseTime": response_time}


async def translator_stream(text: str, direction: str):
    # Retrieve environment variables
    text_data = f"<2{direction}>{text}"
    url = f"{MT_MODEL_URL}/generate_stream"

    

    # Define the event stream generator
    async def event_stream():
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

    return StreamingResponse(event_stream(), media_type="text/event-stream")

