from fastapi import APIRouter, HTTPException,Request,Query,UploadFile,File,Form
# from v1.utils.speech_recognition import speech_to_text_tibetan,speech_to_text_english
from v1.libs.get_buffer import get_buffer
from pydantic import BaseModel
from typing import Optional, List, Tuple
from v1.utils.utils import get_client_metadata
from v1.model.create_inference import create_speech_to_text
from v1.model.edit_inference import edit_inference
import asyncio
import uuid
import ffmpeg
import os
import base64
import httpx
import tempfile
from v1.utils.mixPanel_track import track_user_input
from v1.libs.upload_file_to_s3 import upload_file_to_s3
from v1.utils.get_userId_from_cookie import get_user_id_from_cookie
from datetime import datetime
from io import BytesIO
import re
from pydub import AudioSegment

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

class Base64Input(BaseModel):
    input: str
    lang: str
    
@router.post("/file")
async def speech_to_text_func(
    client_request: Request,
    file: UploadFile = File(...),  # Upload file directly
    lang: str = Form(...)           # Language as a form field
):
    user_id = await get_user_id_from_cookie(client_request)

    try:
        audio = await file.read()
        
        flac_audio, flac_filename = await convert_to_flac(audio, file.filename)

        flac_file = tempfile.NamedTemporaryFile(delete=False)
        file_url = ""
        try:
            flac_file.write(flac_audio)
            flac_file.seek(0)
            file_url = await upload_file_to_s3(flac_file, 'audio/flac', 'stt/' + flac_filename)
        finally:
            flac_file.close()
            os.unlink(flac_file.name)

        # --- Chunk, transcribe, and dedupe overlapping text ---
        chunks = await split_flac_with_overlap(
            flac_audio,
            chunk_seconds=30,
            overlap_seconds=0.5,
        )

        aggregated_text_parts = []
        response_times = []
        for idx, chunk_bytes in enumerate(chunks):
            text_part, chunk_rt = await transcribe_audio(chunk_bytes)
            text_part = (text_part or "").strip()
            if aggregated_text_parts:
                text_part = merge_chunk_text(aggregated_text_parts[-1], text_part)
            aggregated_text_parts.append(text_part)
            response_times.append(chunk_rt)

        text_data = " ".join(part for part in aggregated_text_parts if part)
        response_time = round(sum(response_times), 4)

        client_ip, source_app, city, country = get_client_metadata(client_request)
        generated_id = str(uuid.uuid4())

        stt_data = {
            "id": generated_id,
            "input": file_url,
            "output": text_data,
            "response_time": response_time,
            "ip_address": client_ip,
            "version": "wav2vec2_run10",
            "source_app": source_app,
            "user_id": user_id,
            "city": city,
            "country": country,
        }

        mixPanel_data = {
            "user_id": user_id or "random_user",
            "type": "SpeechToText",
            "input": file_url,
            "output": text_data,
            "ip_address": client_ip,
            "city": city,
            "country": country,
            "response_time": response_time,
            "version": "1.0.0",
            "source_app": source_app,
        }

        loop = asyncio.get_event_loop()

        # Schedule create_speech_to_text safely
        if asyncio.iscoroutinefunction(create_speech_to_text):
            loop.create_task(create_speech_to_text(stt_data))
        else:
            loop.run_in_executor(None, create_speech_to_text, stt_data)

        # Schedule track_user_input safely
        if asyncio.iscoroutinefunction(track_user_input):
            loop.create_task(track_user_input(mixPanel_data, client_request))
        else:
            loop.run_in_executor(None, track_user_input, mixPanel_data, client_request)

        return {
            "success": True,
            "id": generated_id,
            "file": file_url,
            "output": text_data,
            "responseTime": response_time,
        }

    except Exception as e:
        import traceback
        print("❌ [ERROR] Exception during audio processing:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"audio processing failed: {str(e)}")
            

@router.post("/")
async def speech_to_text_func(request:Input, client_request: Request):
       user_id=await get_user_id_from_cookie(client_request)
    
       try:
        audio_url=request.input
        audio=await get_buffer(audio_url)
        client_ip, source_app,city,country = get_client_metadata(client_request)
        flac_audio, flac_filename = await convert_to_flac(audio, request.input)
        # --- Chunk, transcribe, and dedupe overlapping text ---
        chunks = await split_flac_with_overlap(
            flac_audio,
            chunk_seconds=30,
            overlap_seconds=0.5,
        )

        aggregated_text_parts = []
        response_times = []
        for idx, chunk_bytes in enumerate(chunks):
            text_part, chunk_rt = await transcribe_audio(chunk_bytes)
            text_part = (text_part or "").strip()
            if aggregated_text_parts:
                text_part = merge_chunk_text(aggregated_text_parts[-1], text_part)
            aggregated_text_parts.append(text_part)
            response_times.append(chunk_rt)

        text_data = " ".join(part for part in aggregated_text_parts if part)
        response_time = round(sum(response_times), 4)
        
        generated_id=  str(uuid.uuid4())
        stt_data = {
        "id":generated_id,
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
        
        mixPanel_data = {
                    "user_id": user_id, 
                    "type": 'SpeechToText',
                    "input": request.input,
                    "output": text_data,
                    "ip_address": client_ip,
                    "city": city,
                    "country": country,
                    "response_time": response_time,
                    "version": "1.0.0",
                    "source_app": source_app,
                }
        if user_id is None:
            mixPanel_data['user_id'] = "random_user"
        tracked_event = track_user_input(mixPanel_data, client_request)
        
        loop = asyncio.get_event_loop()
        if asyncio.iscoroutinefunction(create_speech_to_text):
            loop.create_task(create_speech_to_text(stt_data))
        else:
            loop.run_in_executor(None, create_speech_to_text, stt_data)
        return {
            "success": True,
            "id":generated_id,
            "output": text_data,
            "responseTime": response_time,
        }
    
       except Exception as e:
           import traceback
           print("[ERROR] Exception during /api/v1/stt processing:")
           traceback.print_exc()
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


import base64

async def transcribe_audio(audio_bytes: bytes):
    """
    Transcribe Tibetan audio using the Hugging Face endpoint that expects base64 input.
    """
    
    MODEL_AUTH = os.getenv("MODEL_AUTH")
    MODEL_URL = os.getenv("STT_MODEL_URL_TIBETAN") 

    if not MODEL_AUTH or not MODEL_URL:
        raise HTTPException(status_code=500, detail="Missing MODEL_AUTH or STT_MODEL_URL_TIBETAN in environment")

    headers = {
        "Authorization": f"Bearer {MODEL_AUTH}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Encode audio as base64
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    payload = {
        "inputs": audio_b64
    }
    
    try:
        start_time = asyncio.get_event_loop().time()

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(MODEL_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        end_time = asyncio.get_event_loop().time()
        response_time = end_time - start_time
        

        # Hugging Face models usually return text under 'text' key
        text = data.get("text", "")
        print(text)
        return text, round(response_time * 1000, 4)

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech-to-text failed: {str(e)}") 


    # if lang and lang != 'bo':
    #     # Call Whisper if a specific language is provided and it's not 'bo'
    #     text_data =await speech_to_text_english(audio)
    #     response_time = round(text_data['response_time'] * 1000, 4)
    # else:
    #     # Call general speech-to-text function for language 'bo'
    #     text_data = await speech_to_text_tibetan(audio)
    #     response_time = round(text_data['response_time'] * 1000, 4)
    # text_data = text_data['text']
    # return text_data, response_time

async def convert_to_flac(audio_data: bytes, input_filename: str) -> Tuple[bytes, str]:
    """
    Convert uploaded audio to FLAC format using ffmpeg
    Returns the FLAC audio data and the new filename
    """
    input_temp = None
    output_temp = None
    flac_data = None
    
    try:
        # Normalize the provided name so it works even if it's a full URL
        safe_name = input_filename or "audio.webm"

        # Strip query string / fragment if a URL was passed
        safe_name = safe_name.split("?", 1)[0].split("#", 1)[0]

        # Take only the basename (in case a full path/URL was provided)
        safe_name = os.path.basename(safe_name) or "audio.webm"

        # Derive a safe extension for the temporary input file
        ext = os.path.splitext(safe_name)[1] or ".webm"
        # Extra safety: remove characters that are invalid in Windows filenames
        ext = "".join(ch for ch in ext if ch.isalnum() or ch in [".", "_"])
        if not ext.startswith("."):
            ext = "." + ext

        # Create temporary files
        input_temp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        output_temp = tempfile.NamedTemporaryFile(suffix='.flac', delete=False)
        
        # Write input audio to temporary file and close it immediately
        input_temp.write(audio_data)
        input_temp.close()
        output_temp.close()
        
        # Run ffmpeg conversion
        stream = ffmpeg.input(input_temp.name)
        stream = ffmpeg.output(stream, output_temp.name, acodec='flac', ac=1, ar='16k')
        ffmpeg.run(stream, capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        # Read the converted FLAC file
        with open(output_temp.name, 'rb') as flac_file:
            flac_data = flac_file.read()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Build a safe output filename (used only for S3 key / logging)
        base_name = os.path.splitext(safe_name)[0] or "audio"
        invalid_chars = '<>:"/\\|?*'
        base_name = "".join(ch for ch in base_name if ch not in invalid_chars) or "audio"

        new_filename = f"{base_name}_{timestamp}.flac"
        return flac_data, new_filename
            
    except ffmpeg.Error as e:
        raise HTTPException(
            status_code=400,
            detail=f"Audio conversion failed: {e.stderr.decode() if e.stderr else str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Audio processing failed: {str(e)}"
        )
    finally:
        # Clean up temporary files with proper error handling
        if input_temp and os.path.exists(input_temp.name):
            try:
                os.unlink(input_temp.name)
            except Exception as e:
                print(f"Warning: Failed to delete temporary input file: {e}")
        
        if output_temp and os.path.exists(output_temp.name):
            try:
                os.unlink(output_temp.name)
            except Exception as e:
                print(f"Warning: Failed to delete temporary output file: {e}")


# --- Exact overlap merge: trims only identical suffix/prefix content ---
def merge_chunk_text(previous: str, current: str) -> str:
    """
    Deterministic overlap removal that only trims when an exact match is found.
    """
    def tibetan_syllables(text: str) -> List[str]:
        normalized = re.sub(r"\s+", " ", text).strip()
        if not normalized:
            return []
        # Insert spaces after Tibetan tsek to separate syllables like སྐབས་སུ
        normalized = normalized.replace("་", "་ ")
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized.split() if normalized else []

    if not previous or not current:
        return current

    prev_norm = re.sub(r"\s+", " ", previous).strip()
    curr_norm = re.sub(r"\s+", " ", current).strip()

    if not prev_norm or not curr_norm:
        return current

    prev_syllables = tibetan_syllables(prev_norm)
    curr_syllables = tibetan_syllables(curr_norm)

    if not prev_syllables or not curr_syllables:
        return current

    max_window = min(20, len(prev_syllables), len(curr_syllables))

    for window in range(max_window, 0, -1):
        if prev_syllables[-window:] == curr_syllables[:window]:
            trimmed = curr_syllables[window:]
            return " ".join(trimmed)

    prev_tail = prev_norm[-120:]
    curr_head = curr_norm[:120]
    match_length = 0
    max_prefix = min(len(prev_tail), len(curr_head))

    for i in range(max_prefix):
        if prev_tail[i] == curr_head[i]:
            match_length += 1
        else:
            break

    if match_length > 0:
        target_chars = curr_head[:match_length]
        char_count = 0
        trim_syllables = 0
        for syllable in curr_syllables:
            char_count += len(syllable)
            trim_syllables += 1
            if char_count >= len(target_chars):
                break
        trimmed = curr_syllables[trim_syllables:]
        return " ".join(trimmed)

    return current


# --- Split FLAC audio into chunks that keep N seconds of overlap ---
async def split_flac_with_overlap(
    flac_bytes: bytes,
    chunk_seconds: float = 30.0,
    overlap_seconds: float = 0.5,
) -> List[bytes]:
    """
    Split FLAC bytes into overlapping chunks to preserve context between segments.
    """
    if overlap_seconds >= chunk_seconds:
        raise ValueError("overlap_seconds must be smaller than chunk_seconds")

    audio = AudioSegment.from_file(BytesIO(flac_bytes), format="flac")
    chunk_ms = int(chunk_seconds * 1000)
    step_ms = int((chunk_seconds - overlap_seconds) * 1000)

    segments: List[bytes] = []
    start = 0
    duration = len(audio)

    while start < duration:
        end = min(start + chunk_ms, duration)
        segment = audio[start:end]
        buffer = BytesIO()
        segment.export(buffer, format="flac")
        segments.append(buffer.getvalue())

        if end == duration:
            break
        start += step_ms

    return segments