
import os
import httpx
import json
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from v1.utils.get_translation_from_file import get_translation_from_file,count_words
from v1.utils.language_detect import detect_language
import time
import re
from mixpanel import Mixpanel
load_dotenv()
MODEL_AUTH = os.getenv('MODEL_AUTH')
MT_MODEL_URL = os.getenv('MT_MODEL_URL')
LLM_MODEL_URL= os.getenv('LLM_MODEL_URL')
MIXPANEL_TOKEN = os.getenv('MIXPANEL_TOKEN')
llm_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
    }
headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MODEL_AUTH}",
        "Access-Control-Allow-Origin": "*",
    }
def clean_text(original_text):
    # Replace the escape sequence for single quotes with just a single quote
    cleaned_text = original_text.replace("\\'", "'")
    
    # Remove unwanted trailing text (customize this pattern based on actual needs)
    cleaned_text = re.sub(r'\s*what to do GARCÍA past , present , and and my\s*$', '', cleaned_text)
    
    # Normalize whitespace
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    # Strip leading and trailing whitespace
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text
    

async def translator_llm(text: str, direction: str ):
    url = LLM_MODEL_URL
    received_data = ""
    response_time = 0
    is_tibetan:bool=detect_language(text)==direction
    # word_count = count_words(text,is_tibetan)
    
    if is_tibetan:
         return {"translation": text, "responseTime": 0}
    # if word_count <= 3:
    #     translation = get_translation_from_file(text,direction)
    #     if translation and translation.strip():
    #        return {"translation": translation, "responseTime": response_time}
    
   

    language = 'Tibetan' if direction == 'bo' else 'English'
    try:
        start_time = time.time()  # Record start time
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={
                    "inputs": text,
                    "lang":language
                },
                headers=llm_headers,
            )
        if response.status_code != 200:
            raise Exception("status code not 200")
        
        translation = response.text
        response_time = round((time.time() - start_time) * 1000, 4)
        received_data = translation
    
    except Exception as e:
        raise Exception(e) from e
    
    
    translation = received_data
   
    return {"translation": translation, "responseTime": response_time}


async def translator_stream_llm(text: str, direction: str,inferenceID, on_complete=None):
    # Retrieve environment variables
    start_time = time.time()
    url = f"{LLM_MODEL_URL}/translation_generate_stream"
     # Retrieve the Origin and Referer headers
    is_tibetan:bool=detect_language(text)==direction
    word_count = count_words(text,is_tibetan)
    # If the text has two or fewer words, try to get the translation from the file
    # if word_count <= 2:
    #     translation = get_translation_from_file(text, direction)
    #     if translation and translation.strip():  # Only stream if a translation is found
    #         async def short_event_stream():
    #             yield f"data: {json.dumps({'generated_text': translation,'id':inferenceID})}\n\n"
    #             if on_complete:
    #                 await on_complete(translation, 0)
    #         return StreamingResponse(short_event_stream(), media_type="text/event-stream")

    # Define the event stream generator
    async def event_stream():
        
        try:
            language = 'Tibetan' if direction == 'bo' else 'English'

            
            body = {
                "inputs": text,
                "lang":language
            }

            async with httpx.AsyncClient() as client:
                async with client.stream("POST", url, json=body, headers=llm_headers) as response:
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
                                try:
                                    parsed_data = json.loads(json_data)
                                except json.JSONDecodeError as e:
                                    print(f"Error decoding JSON: {str(e)}")
                                    continue
                                text_value = parsed_data.get("text", "")
                                generated_text = parsed_data.get("generated_text")
                              
                                if text_value:
                                    yield f"data: {json.dumps({'text': text_value,'id':inferenceID})}\n\n"

                                # Yield the generated text as an SSE event and end the stream
                                if generated_text:
                                    yield f"data: {json.dumps({'generated_text': generated_text,'id':inferenceID})}\n\n"
                                   
                                    return
        except Exception as e:
            yield f"event: error\ndata: Stream error: {str(e)}\n\n"
        
        finally:
            end_time = time.time()  # Capture the end time
            response_time = round((end_time - start_time) * 1000, 4)
            if on_complete:
                if generated_text:
                   await on_complete(generated_text or '', response_time)  # Use empty string if no generated_text


    return StreamingResponse(event_stream(), media_type="text/event-stream")

 

async def translator_mt(text: str, direction: str ):
    url = MT_MODEL_URL
    received_data = ""
    response_time = 0
    is_tibetan:bool=detect_language(text)==direction
    word_count = count_words(text,is_tibetan)
    
    if is_tibetan:
         return {"translation": text, "responseTime": 0}
    if word_count <= 3:
        translation = get_translation_from_file(text,direction)
        if translation and translation.strip():
           return {"translation": translation, "responseTime": response_time}
    
    text_data = clean_text(f'<2{direction}>{text}')
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
            print(response)
        if response.status_code != 200:
            raise Exception("status code not 200")
        
        response_data = response.json()
        response_time = round((time.time() - start_time) * 1000, 4)
        received_data = response_data[0].get('generated_text', '')
    
    except Exception as e:
        raise Exception(e) from e
    
    
    translation = received_data
   
    return {"translation": translation, "responseTime": response_time}


async def translator_stream_mt(text: str, direction: str,inferenceID, on_complete=None):
    # Retrieve environment variables
    text_data =clean_text(f'<2{direction}>{text}')
    start_time = time.time()
    url = f"{MT_MODEL_URL}/generate_stream"
     # Retrieve the Origin and Referer headers
    is_tibetan:bool=detect_language(text)==direction
    word_count = count_words(text,is_tibetan)
    mp = Mixpanel("YOUR_TOKEN")
    # If the text has two or fewer words, try to get the translation from the file
    if word_count <= 2:
        translation = get_translation_from_file(text, direction)
        if translation and translation.strip():  # Only stream if a translation is found
            async def short_event_stream():
                yield f"data: {json.dumps({'generated_text': translation,'id':inferenceID})}\n\n"
                if on_complete:
                    await on_complete(translation, 0)
            return StreamingResponse(short_event_stream(), media_type="text/event-stream")

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
                                    yield f"data: {json.dumps({'text': text_value,'id':inferenceID})}\n\n"

                                # Yield the generated text as an SSE event and end the stream
                                if generated_text:
                                    yield f"data: {json.dumps({'generated_text': generated_text,'id':inferenceID})}\n\n"
                                    return
        except Exception as e:
            yield f"event: error\ndata: Stream error: {str(e)}\n\n"
        
        finally:
            end_time = time.time()  # Capture the end time
            response_time = round((end_time - start_time) * 1000, 4)
            if on_complete:
                if generated_text:
                   await on_complete(generated_text or '', response_time)  # Use empty string if no generated_text


    return StreamingResponse(event_stream(), media_type="text/event-stream")