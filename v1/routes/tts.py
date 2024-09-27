from fastapi import APIRouter, HTTPException,Request,Query
from v1.utils.text_audio import tibetan_synthesizer
from pydantic import BaseModel
from v1.libs.upload_file_to_s3 import upload_file_to_s3
from v1.model.create_inference import create_text_to_speech
import uuid
import time
from v1.utils.utils import get_client_metadata
from typing import Optional
from v1.utils.utils import get_user_id
from v1.libs.chunk_text import chunk_tibetan_text
from v1.model.edit_inference import edit_inference
from pydub import AudioSegment
from v1.utils.get_id_token import get_id_token
import base64
import io
import asyncio

router = APIRouter()
class Input(BaseModel):
    input: str

 

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
    token=get_id_token(client_request)
    user_id =await get_user_id(token)

    try:
        chunked_text= chunk_tibetan_text(request.input)
        audio_data =await process_text_chunks(chunked_text)
        file_url = await handle_audio_file(audio_data["audio"])
        print(file_url)
        client_ip, source_app,city,country = get_client_metadata(client_request)
        response_time = round(audio_data['response_time'] * 1000, 4)
        tts_data = {
        "input": request.input,
        "output": file_url,
        "response_time": response_time,
        "ip_address": client_ip,
        "version": None,
        "source_app": source_app,
        "user_id": user_id,
        "city": city,
        "country": country,
        }
        data= await create_text_to_speech( tts_data)
        
        # Return the result
        return {
            "success": True,
            "output": file_url,
            "id": data.id,
            "responseTime": response_time,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio failed: {str(e)}")



@router.put("/{id}")
async def update_ocr(id: int, action: str = Query(..., description="Action to perform: 'like', or 'dislike'")):

    # Call the edit_inference function to update the record in ocr table
    updated_record = await edit_inference('texttospeechs', id, action,None)

    if not updated_record:
        raise HTTPException(status_code=404, detail="Record not found")

    return {"message": f"Record {action}d successfully", "data": updated_record}





async def handle_audio_file(base64_audio):
    audio_file = io.BytesIO(base64_audio)
    timestamp = int(time.time())
    file_name = f"TTS/output/{timestamp}_{uuid.uuid4()}-tts-audio.wav"
    file_url = await upload_file_to_s3(audio_file, "audio/wav", file_name)
    return file_url

async def process_text_chunks(text_chunks, volume_increase_db=20):
    audio_chunks = []
    response_time = 0
    start_time = asyncio.get_event_loop().time()  # Record start time
    for i, chunk in enumerate(text_chunks):
        try:
            audio_string = await tibetan_synthesizer(chunk)
            if isinstance(audio_string, dict) and 'audio' in audio_string:
                # Decode the base64-encoded audio string
                audio_data = base64.b64decode(audio_string['audio'])

                # Load the audio segment from the decoded audio data
                audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="wav")

                # Ensure the audio segment has the correct format
                audio_segment = audio_segment.set_frame_rate(44100).set_channels(1).set_sample_width(2)
                audio_segment = audio_segment + volume_increase_db
                # Append the audio segment to the list
                audio_chunks.append(audio_segment)
            else:
                print(f"Chunk {i}: Invalid response format from tibetan_synthesizer")
        except Exception as e:
            print(f"Error processing chunk {i}: {str(e)}")


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
    
