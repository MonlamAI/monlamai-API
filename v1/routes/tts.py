from fastapi import APIRouter, HTTPException,Request,Query,BackgroundTasks
from v1.utils.text_audio import tibetan_synthesizer
from pydantic import BaseModel
from v1.libs.upload_file_to_s3 import upload_file_to_s3
from v1.model.create_inference import create_text_to_speech
import uuid
import time
from v1.utils.utils import get_client_metadata
from v1.utils.utils import get_user_id
from v1.libs.chunk_text import chunk_tibetan_text
from v1.model.edit_inference import edit_inference
from pydub import AudioSegment
from v1.utils.get_id_token import get_id_token
import base64
import io
import asyncio
from fastapi.responses import StreamingResponse, HTMLResponse
import json
from io import BytesIO

router = APIRouter()
class Input(BaseModel):
    input: str

 

@router.get("/")
async def check_text_to_speech(input:str):
       text=input; 
       try:
        audio_data = await tibetan_synthesizer(
            text
        )

        return {
            "success": True,
            "responseTime": audio_data['response_time'],
            "audio": audio_data['audio'],
        }
    
       except Exception as e:
        raise HTTPException(status_code=500, detail=f"audio failed: {str(e)}")

@router.post("/")
async def text_to_speech(request: Input, client_request: Request):
    token=get_id_token(client_request)
    user_id =await get_user_id(token)

    try:
        chunked_text= chunk_tibetan_text(request.input)
        generated_id=  uuid.uuid4()
        print(generated_id)
        audio_data =await process_text_chunks(chunked_text)
        file_url = await handle_audio_file(audio_data["audio"])
        client_ip, source_app,city,country = get_client_metadata(client_request)
        response_time = round(audio_data['response_time'] * 1000, 4)
        tts_data = {
        "id":generated_id,
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
        asyncio.create_task(create_text_to_speech( tts_data))
        
        # Return the result
        return {
            "success": True,
            "output": file_url,
            "id": generated_id,
            "responseTime": response_time,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio failed: {str(e)}")



@router.post("/stream")
async def stream_endpoint(request: Input, client_request: Request):
    client_ip, source_app,city,country = get_client_metadata(client_request)
    token=get_id_token(client_request)
    user_id =await get_user_id(token)
    chunked_text= chunk_tibetan_text(request.input,max_chunk_size=100)
        
 # Define on_complete as an async function to avoid issues
    async def on_complete(output, response_time):
        generated_id=  uuid.uuid4()
        tts_data = {
             "id":generated_id,
            "input": request.input,
            "output": output,
            "response_time": response_time,
            "ip_address": client_ip,
            "version": None,
            "source_app": source_app,
            "user_id": user_id,
            "city": city,
            "country": country,
        }
        # Use asyncio to create a task for the asynchronous function
        asyncio.create_task(create_text_to_speech(tts_data))
                 
    return StreamingResponse(process_text_chunks_stream(chunked_text,volume_increase_db=20,on_complete=on_complete), media_type="text/event-stream")
# Helper function to update TTS data after streaming (to be called separately)

async def process_text_chunks_stream(text_chunks, volume_increase_db=20,on_complete=None):
    response_time = 0
    start_time = asyncio.get_event_loop().time()
    urls=[]
    try:
        for i, chunk in enumerate(text_chunks):
            try:
                audio_string = await tibetan_synthesizer(chunk)
                if isinstance(audio_string, dict) and 'audio' in audio_string:
                    
                    audio_data = audio_string['audio']
                    if isinstance(audio_data, str):
                        # If it's a base64 string, decode it to bytes
                        try:
                            audio_bytes = base64.b64decode(audio_data)
                        except Exception as e:
                            print(f"Failed to decode base64 string: {str(e)}")
                            yield f'data: {json.dumps({"error": "Invalid audio format"})}\n\n'
                            continue
                    else:
                        # If it's already bytes, use it directly
                        audio_bytes = audio_data
                    audio_data = io.BytesIO(audio_bytes)
                    audio_segment = AudioSegment.from_wav(audio_data)
                    
                    # Process the audio segment
                    processed_audio = (
                        audio_segment
                        .set_frame_rate(44100)
                        .set_channels(1)
                        .set_sample_width(2)
                    ) + volume_increase_db

                    # Export the processed segment as webm
                    output_buffer = io.BytesIO()
                    processed_audio.export(output_buffer, format="webm")
                    output_buffer.seek(0)

                    # Upload the audio and get the file URL
                    file_url = await handle_audio_file(output_buffer.getvalue())

                    # Yield the file URL for this chunk
                    if file_url:
                        urls.append(file_url)
                        yield f'data: {json.dumps({"output": file_url,"inference_id":123})}\n\n'
                        print(f"Processed chunk {i}: {file_url}")
                    else:
                        print(f"Chunk {i}: No file URL returned from handle_audio_file")
                        yield f'data: {json.dumps({"error": "Failed to upload audio file"})}\n\n'

                else:
                    error_msg = f"Chunk {i}: Invalid response format from tibetan_synthesizer"
                    print(error_msg)
                    yield f'data: {json.dumps({"error": error_msg})}\n\n'

            except Exception as e:
                error_msg = f"Error processing chunk {i}: {str(e)}"
                print(error_msg)
                yield f'data: {json.dumps({"error": error_msg})}\n\n'
                continue

        # Calculate response time
        end_time = asyncio.get_event_loop().time()
        response_time = end_time - start_time

        # Send final messages
        yield f'data: {json.dumps({"response_time": response_time})}\n\n'
        print(f'Processing completed in {response_time:.2f} seconds')
        yield f'data: {json.dumps({"done": True})}\n\n'
        yield '[DONE]'
    except Exception as e:
            yield f"event: error\ndata: Stream error: {str(e)}\n\n"
    finally:
        if on_complete:
            if len(urls)>0:
               await on_complete(json.dumps(urls), response_time)
  

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
    file_name = f"TTS/output/{timestamp}_{uuid.uuid4()}-tts-audio.webm"
    file_url = await upload_file_to_s3(audio_file, 'audio/webm', file_name)
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
    
