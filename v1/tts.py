from fastapi import APIRouter, HTTPException,Request
from v1.utils.text_audio import tibetan_synthesizer
from pydantic import BaseModel
from v1.libs.upload_file_to_s3 import upload_file_to_s3
from v1.libs.base64_to_file_buffer import base64_to_file_buffer
from v1.model.create_inference import create_text_to_speech
import uuid
from db import get_db
import time
from v1.utils.utils import get_client_metadata
from typing import Optional
from v1.utils.utils import get_user_id
from v1.libs.chunk_text import chunk_tibetan_text
from pydub import AudioSegment
import base64
import io
import asyncio

router = APIRouter()
class Input(BaseModel):
    input: str
    id_token:Optional[str] = None

 

@router.get("/")
async def check_text_to_speech():
       text="ངའི་མིང་ལ་ཀུན་བཟང་རེད་།" 
       try:
        audio_data = await tibetan_synthesizer(
            text
        )

        return {
            "success": True,
            "audio": audio_data['audio'],
            "responseTime": audio_data['response_time'],
        }
    
       except Exception as e:
        raise HTTPException(status_code=500, detail=f"audio failed: {str(e)}")

@router.post("/")
async def text_to_speech(request: Input, client_request: Request):
    token = request.id_token
    user_id = get_user_id(token)

    try:
        chunked_text= chunk_tibetan_text(request.input)
        audio_data =await process_text_chunks(chunked_text)
    
        file_url = await handle_audio_file(audio_data["audio"])

        client_ip, source_app = get_client_metadata(client_request)

        db = next(get_db())
        response_time = round(audio_data['response_time'] * 1000, 4)
        save_tts_data(db, request.input, file_url, response_time, client_ip, source_app, user_id)

        # Return the result
        return {
            "success": True,
            "output": file_url,
            "responseTime": response_time,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio failed: {str(e)}")


async def handle_audio_file(base64_audio):
    audio_file = io.BytesIO(base64_audio)
    timestamp = int(time.time())
    file_name = f"TTS/output/{timestamp}_{uuid.uuid4()}-tts-audio.wav"
    file_url = await upload_file_to_s3(audio_file, "audio/wav", file_name)
    return file_url

async def process_text_chunks(text_chunks):
    audio_chunks = []
    response_time = 0
    start_time = asyncio.get_event_loop().time()  # Record start time
    for i, chunk in enumerate(text_chunks):
        try:
            amplified_audio_string = await tibetan_synthesizer(chunk)
            if isinstance(amplified_audio_string, dict) and 'audio' in amplified_audio_string:
                # Decode the base64-encoded audio string
                audio_data = base64.b64decode(amplified_audio_string['audio'])

                # Load the audio segment from the decoded audio data
                audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="wav")

                # Ensure the audio segment has the correct format
                audio_segment = audio_segment.set_frame_rate(44100).set_channels(1).set_sample_width(2)

                # Append the audio segment to the list
                audio_chunks.append(audio_segment)
            else:
                print(f"Chunk {i}: Invalid response format from tibetan_synthesizer")
        except Exception as e:
            print(f"Error processing chunk {i}: {str(e)}")

    print(f'Number of chunks: {len(audio_chunks)}')

    if not audio_chunks:
        raise ValueError("No valid audio chunks were processed")

    try:
        # Merge all audio segments
        merged_audio = sum(audio_chunks)
        

       # Export merged audio to a BytesIO object
        merged_audio_io = io.BytesIO()
        merged_audio.export(merged_audio_io, format="wav")

        # Get the byte value and print its length
        audio_bytes = merged_audio_io.getvalue()
        end_time = asyncio.get_event_loop().time()  # Record end time
        response_time = end_time - start_time  # Calculate response time
          
        # Return the merged audio as bytes
        return {
         "audio":   audio_bytes,
         "response_time": response_time
        }
    except Exception as e:
        print(f"Error during audio merging: {str(e)}")
        raise
    
def save_tts_data(db, input_text, file_url, response_time, client_ip, source_app, user_id):
    tts_data = {
        "input": input_text,
        "output": file_url,
        "response_time": response_time,
        "ip_address": client_ip,
        "version": None,
        "source_app": source_app,
        "user_id": user_id,
    }
    create_text_to_speech(db, tts_data)