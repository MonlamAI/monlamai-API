from fastapi import APIRouter, HTTPException,Request,Query,UploadFile,File,Form
from v1.utils.speech_recognition import speech_to_text_tibetan,speech_to_text_english
from v1.libs.get_buffer import get_buffer
from pydantic import BaseModel
from v1.utils.utils import get_user_id
from typing import Optional
from v1.utils.utils import get_client_metadata
from v1.model.create_inference import create_speech_to_text
from v1.model.edit_inference import edit_inference
from v1.utils.get_id_token import get_id_token
import asyncio
import uuid
import ffmpeg
import os 
import tempfile
from typing import Tuple
from v1.utils.mixPanel_track import track_signup_input,track_user_input
from v1.libs.upload_file_to_s3 import upload_file_to_s3


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
    token = get_id_token(client_request)
    user_id = await get_user_id(token)
    
    try:
        # Read the audio content from the uploaded file
        audio = await file.read()
        content_type = file.content_type
        flac_audio, flac_filename = await convert_to_flac(audio, file.filename)
        file_url = await upload_file_to_s3(file.file, content_type, 'stt/'+file.filename)
        client_ip, source_app, city, country = get_client_metadata(client_request)
        text_data, response_time = await transcribe_audio(flac_audio, lang )
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
        
        # Asynchronously create the speech-to-text record
        mixPanel_data = {
                    "user_id": user_id, 
                    "type": 'SpeechToText',
                    "input": file_url,
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
        # asyncio.create_task(create_speech_to_text(stt_data))
        await create_speech_to_text(stt_data)
        
        return {
            "success": True,
            "id": generated_id,
            "output": text_data,
            "responseTime": response_time,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"audio processing failed: {str(e)}")
            
     
           



@router.post("/")
async def speech_to_text_func(request:Input, client_request: Request):
       token = get_id_token(client_request)
       user_id =await get_user_id(token)
       try:
        audio_url=request.input
        lang=request.lang
        audio=await get_buffer(audio_url)
        client_ip, source_app,city,country = get_client_metadata(client_request)
        text_data, response_time = await transcribe_audio(audio, lang)
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
        
        asyncio.create_task(create_speech_to_text(stt_data))
        return {
            "success": True,
            "id":generated_id,
            "output": text_data,
            "responseTime": response_time,
        }
    
       except Exception as e:
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




    

async def transcribe_audio(audio, lang):
    if lang and lang != 'bo':
        # Call Whisper if a specific language is provided and it's not 'bo'
        text_data =await speech_to_text_english(audio)
        response_time = round(text_data['response_time'] * 1000, 4)
    else:
        # Call general speech-to-text function for language 'bo'
        text_data = await speech_to_text_tibetan(audio)
        response_time = round(text_data['response_time'] * 1000, 4)
    text_data = text_data['text']
    return text_data, response_time

async def convert_to_flac(audio_data: bytes, input_filename: str) -> Tuple[bytes, str]:
    """
    Convert uploaded audio to FLAC format using ffmpeg
    Returns the FLAC audio data and the new filename
    """
    input_temp = None
    output_temp = None
    flac_data = None
    
    try:
        # Create temporary files with delete=True (will be deleted when closed)
        input_temp = tempfile.NamedTemporaryFile(suffix=os.path.splitext(input_filename)[1], delete=False)
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
        
        new_filename = os.path.splitext(input_filename)[0] + '.flac'
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