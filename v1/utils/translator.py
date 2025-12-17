
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
import logging

load_dotenv()
MODEL_AUTH = os.getenv('MODEL_AUTH')
MT_MODEL_URL = os.getenv('MT_MODEL_URL')
MT_MODEL_NAME = os.getenv('MT_MODEL_NAME')
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


logging.basicConfig(
    filename="logger.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


language_options = [
    {"value": "English", "code": "en", "name": "english"},
    {"value": "Tibetan", "code": "bo", "name": "tibetan"},
    # {"value": "Sanskrit (Devanagari)", "code": "sa-dev", "name": "sanskrit-dev"},
    {"value": "Traditional Chinese", "code": "zh-old", "name": "traditional-chinese"},
    {"value": "Hindi", "code": "hi", "name": "hindi"},
    {"value": "Japanese", "code": "ja", "name": "japanese"},
    # {"value": "Korean", "code": "ko", "name": "korean"},
    # {"value": "Pali", "code": "pi", "name": "pali"},
    {"value": "Simplified Chinese", "code": "zh-new", "name": "simplified-chinese"},
    # {"value": "Russian", "code": "ru", "name": "russian"},
    {"value": "French", "code": "fr-new", "name": "french"},
    {"value": "German", "code": "de", "name": "german"},
    # {"value": "Italian", "code": "it", "name": "italian"},
    # {"value": "Spanish", "code": "es", "name": "spanish"},
    # {"value": "Portuguese", "code": "pt", "name": "portuguese"},
    # {"value": "Dutch", "code": "nl", "name": "dutch"},
    {"value": "Czech", "code": "cs", "name": "czech"},
    {"value": "Vietnamese", "code": "vi", "name": "vietnamese"},
    # {"value": "Mongolian", "code": "mn", "name": "mongolian"},
]

translation_cache = {}

def detect_language_from_code(code):
    for option in language_options:
        if option["code"] == code:
            return option["value"]
    return "English"

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
    word_count = count_words(text,is_tibetan)
    
    if is_tibetan:
         return {"translation": text, "responseTime": 0}
    print(word_count)
    if word_count <= 3:
            translation = get_translation_from_file(text,direction)
            if translation and translation.strip():
                return {"translation": translation, "responseTime": response_time}
    language =  detect_language_from_code(direction)
    
    try:
        start_time = time.time()  # Record start time
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url+'/translation',
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


async def translator_stream_llm(text: str, direction: str, inferenceID, on_complete=None):
    # Retrieve environment variables
    start_time = time.time()
    url = f"{LLM_MODEL_URL}/translation_generate_stream"
    language = detect_language_from_code(direction)
    is_tibetan = detect_language(text) == direction
    word_count = count_words(text, is_tibetan)
    
    if word_count <= 2:
        translation = get_translation_from_file(text, direction)
        if translation and translation.strip():  # Only stream if a translation is found
            async def short_event_stream():
                yield f"data: {json.dumps({'generated_text': translation, 'id': inferenceID})}\n\n"
                if on_complete:
                    await on_complete(translation, 0)
            return StreamingResponse(short_event_stream(), media_type="text/event-stream")

    async def event_stream():
        generated_text = ""
        try:
            body = {
                "inputs": text,
                "lang": language
            }
            
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("POST", url, json=body, headers=llm_headers) as response:
                    buffer = ""
                    async for chunk in response.aiter_bytes():
                        buffer += chunk.decode('utf-8', errors='replace')
                        
                        # Process complete lines
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            if line.startswith("data:"):
                                json_data = line[len("data:"):].strip()
                                
                                if not json_data:
                                    continue
                                    
                                try:
                                    # Fix invalid Unicode escape sequences
                                    parsed_data = json.loads(json_data)
                                    text_value = parsed_data.get("text", "")
                                    temp_generated_text = parsed_data.get("generated_text", "")
                                    
                                    if text_value:
                                        yield f"data: {json.dumps({'text': text_value, 'id': inferenceID})}\n\n"
                                    
                                    if temp_generated_text:
                                        generated_text = temp_generated_text  # Save it for on_complete
                                        yield f"data: {json.dumps({'generated_text': temp_generated_text, 'id': inferenceID})}\n\n"
                                        
                                except json.JSONDecodeError as e:
                                    print(f"Error decoding JSON: {str(e)}, data slice: {json_data[:50]}...")
                                    continue
        
        except Exception as e:
            print(f"Stream error: {str(e)}")
            yield f"event: error\ndata: Stream error: {str(e)}\n\n"
        
        finally:
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 4)
            if on_complete:
                await on_complete(generated_text, response_time)

    return StreamingResponse(event_stream(), media_type="text/event-stream")



# LEGACY_TGI_START: Previous MT implementation (TGI-style generate)
# async def translator_mt(text: str, direction: str ):
#     url = MT_MODEL_URL
#     received_data = ""
#     response_time = 0
#     is_tibetan:bool=detect_language(text)==direction
#     word_count = count_words(text,is_tibetan)
#     if is_tibetan:
#          return {"translation": text, "responseTime": 0}
#     if word_count <= 3:
#         translation = get_translation_from_file(text,direction)
#         if translation and translation.strip():
#            return {"translation": translation, "responseTime": response_time}
#     text_data = clean_text(f'<2{direction}>{text}')
#     try:
#         start_time = time.time()
#         async with httpx.AsyncClient() as client:
#             response = await client.post(
#                 url,
#                 json={
#                     "inputs": text_data,
#                     "parameters": {"max_new_tokens": 256},
#                 },
#                 headers=headers,
#             )
#         if response.status_code != 200:
#             raise Exception("status code not 200")
#         response_data = response.json()
#         response_time = round((time.time() - start_time) * 1000, 4)
#         received_data = response_data[0].get('generated_text', '')
#     except Exception as e:
#         raise Exception(e) from e
#     translation = received_data
#     return {"translation": translation, "responseTime": response_time}
# LEGACY_TGI_END

async def translator_mt(text: str, direction: str ):
    url = f"{MT_MODEL_URL}/v1/chat/completions"
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
    target_language = detect_language_from_code(direction)
    
    # Check cache first for identical requests
    cache_key = (text.strip(), direction)
    if cache_key in translation_cache:
        return {"translation": translation_cache[cache_key], "responseTime": 0}

# --- Deterministic translation prompt ---
    prompt = f"""
        You are a professional linguist and translator fluent in all listed languages.
        You translate between the source and target languages indicated below.

        Your translation rules:
        1. Preserve the full meaning, tone, and intent of the text — not just the literal words.
        2. Translate idioms, cultural expressions, and implied meanings naturally (e.g., "It's on the house" → "It's free of charge").
        3. When an expression has no direct equivalent, use a culturally appropriate phrase that conveys the same intent.
        4. Keep grammar, flow, and tone natural in the target language.
        5. Always produce the exact same translation for identical inputs.
        6. Do not add explanations or notes — only output the translation.

        Language codes:
        en = English
        bo = Tibetan
        zh-old = Traditional Chinese
        hi = Hindi
        ja = Japanese
        zh-new = Simplified Chinese
        fr-new = French
        de = German
        cs = Czech
        vi = Vietnamese

        Input:
        target_language: {target_language}
        text: "{text}"

        Output (translation only):
    """.strip()

    try:
        start_time = time.time()  # Record start time
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={
                    "model": MT_MODEL_NAME,
                    "temperature": 0.6,   # 🔒 Make deterministic
                    "top_p": 1,         # 🔒 Make deterministic
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are a deterministic translation model. "
                                "Output only the translated text, without explanations."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                },
                headers=headers,
                timeout=60.0,
            )
        if response.status_code != 200:
            raise Exception(f"status code not 200: {response.status_code} - {response.text}")
        
        response_data = response.json()
        response_time = round((time.time() - start_time) * 1000, 4)
        # OpenAI-compatible response shape
        received_data = (
            (response_data.get('choices') or [{}])[0]
            .get('message', {})
            .get('content', '')
        ).strip()
    
    except Exception as e:
        raise Exception(e) from e
    
    
    translation = received_data
   
    return {"translation": translation, "responseTime": response_time}


# LEGACY_TGI_START: Previous MT streaming implementation (TGI-style generate_stream)
# async def translator_stream_mt(text: str, direction: str,inferenceID, on_complete=None):
#     text_data =clean_text(f'<2{direction}>{text}')
#     start_time = time.time()
#     url = f"{MT_MODEL_URL}/generate_stream"
#     is_tibetan:bool=detect_language(text)==direction
#     word_count = count_words(text,is_tibetan)
#     if word_count <= 2:
#         translation = get_translation_from_file(text, direction)
#         if translation and translation.strip():
#             async def short_event_stream():
#                 yield f"data: {json.dumps({'generated_text': translation,'id':inferenceID})}\n\n"
#                 if on_complete:
#                     await on_complete(translation, 0)
#             return StreamingResponse(short_event_stream(), media_type="text/event-stream")
#     async def event_stream():
#         try:
#             body = {"inputs": text_data, "parameters": {"max_new_tokens": 256}}
#             async with httpx.AsyncClient() as client:
#                 async with client.stream("POST", url, json=body, headers=headers) as response:
#                     async for chunk in response.aiter_bytes():
#                         data = chunk.decode('utf-8').strip()
#                         if not data:
#                             continue
#                         for line in data.split('\n'):
#                             if line.startswith("data:"):
#                                 json_data = line[len("data:"):].strip()
#                                 if not json_data:
#                                     continue
#                                 parsed_data = json.loads(json_data)
#                                 text_value = parsed_data.get("token", {}).get("text")
#                                 generated_text = parsed_data.get("generated_text")
#                                 if text_value:
#                                     yield f"data: {json.dumps({'text': text_value,'id':inferenceID})}\n\n"
#                                 if generated_text:
#                                     yield f"data: {json.dumps({'generated_text': generated_text,'id':inferenceID})}\n\n"
#                                     return
#         except Exception as e:
#             yield f"event: error\ndata: Stream error: {str(e)}\n\n"
#         finally:
#             end_time = time.time()
#             response_time = round((end_time - start_time) * 1000, 4)
#             if on_complete:
#                 if generated_text:
#                     await on_complete(generated_text or '', response_time)
#     return StreamingResponse(event_stream(), media_type="text/event-stream")
# LEGACY_TGI_END

async def translator_stream_mt(text: str, direction: str,inferenceID, on_complete=None):
    # OpenAI-compatible Chat Completions streaming
    start_time = time.time()
    url = f"{MT_MODEL_URL}/v1/chat/completions"
    is_tibetan:bool=detect_language(text)==direction
    word_count = count_words(text,is_tibetan)
    if word_count <= 2:
        translation = get_translation_from_file(text, direction)
        if translation and translation.strip():
            async def short_event_stream():
                yield f"data: {json.dumps({'generated_text': translation,'id':inferenceID})}\n\n"
                if on_complete:
                    await on_complete(translation, 0)
            return StreamingResponse(short_event_stream(), media_type="text/event-stream")

    target_language = detect_language_from_code(direction)
    
    # Check cache first for identical requests
    cache_key = (text.strip(), direction)
    if cache_key in translation_cache:
        cached_translation = translation_cache[cache_key]
        async def cached_event_stream():
            yield f"data: {json.dumps({'generated_text': cached_translation, 'id': inferenceID})}\n\n"
            if on_complete:
                await on_complete(cached_translation, 0)
        return StreamingResponse(cached_event_stream(), media_type="text/event-stream")
    
    # --- Deterministic translation prompt ---
    prompt = f"""
        You are a professional linguist and translator fluent in all listed languages.
        You translate between the source and target languages indicated below.

        Your translation rules:
        1. Preserve the full meaning, tone, and intent of the text — not just the literal words.
        2. Translate idioms, cultural expressions, and implied meanings naturally (e.g., "It's on the house" → "It's free of charge").
        3. When an expression has no direct equivalent, use a culturally appropriate phrase that conveys the same intent.
        4. Keep grammar, flow, and tone natural in the target language.
        5. Always produce the exact same translation for identical inputs.
        6. Do not add explanations or notes — only output the translation.

        Language codes:
        en = English
        bo = Tibetan
        zh-old = Traditional Chinese
        hi = Hindi
        ja = Japanese
        zh-new = Simplified Chinese
        fr-new = French
        de = German
        cs = Czech
        vi = Vietnamese

        Input:
        target_language: {target_language}
        text: "{text}"

        Output (translation only):
    """.strip()

    async def event_stream():
        full_text = ""
        try:
            body = {
                "model": MT_MODEL_NAME, 
                "temperature": 0.6,   #make deterministic
                "top_p": 1,         #make deterministic
                "messages": [
                    {"role": "system", "content": ("You are a deterministic, context-aware translation model. "
                            "Output only the translated text, without explanations."),
                     },
                    {"role": "user", "content": prompt}
                ],
                "stream": True
            }
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("POST", url, json=body, headers=headers) as response:
                    async for raw_line in response.aiter_lines():
                        if raw_line is None:
                            continue
                        line = raw_line.strip()
                        if not line:
                            continue 
                        if not line.startswith("data:"):
                            continue
                        payload = line[len("data:"):].strip()
                        if payload == "[DONE]":
                            break
                        try:
                            chunk = json.loads(payload)
                        except json.JSONDecodeError:
                            continue
                        choices = chunk.get("choices") or []
                        if not choices:
                            continue
                        delta = choices[0].get("delta", {})
                        content = delta.get("content")
                        if content:
                            full_text += content
                            yield f"data: {json.dumps({'text': content,'id':inferenceID})}\n\n"
        except Exception as e:
            yield f"event: error\ndata: Stream error: {str(e)}\n\n"
        finally:
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 4)
            
            # Cache the complete translation
            if full_text.strip():
                translation_cache[cache_key] = full_text.strip()
                
            # Optionally send a final aggregated event for compatibility
            if full_text:
                yield f"data: {json.dumps({'generated_text': full_text,'id':inferenceID})}\n\n"
            if on_complete:
                await on_complete(full_text or '', response_time)

    return StreamingResponse(event_stream(), media_type="text/event-stream")