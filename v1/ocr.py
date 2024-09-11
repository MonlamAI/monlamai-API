from fastapi import APIRouter, HTTPException,Request
from v1.utils.google_ocr import google_ocr
from v1.libs.get_buffer import get_buffer
from pydantic import BaseModel
from v1.libs.get_text import get_text
from typing import Optional
from v1.utils.utils import get_user_id
from v1.utils.utils import get_client_metadata
from v1.model.create_inference import create_ocr
from db import get_db
router = APIRouter()

class Input(BaseModel):
    input: str
    id_token:Optional[str] = None


@router.get("/")
async def check_ocr():
       image_url ="https://s3.ap-south-1.amazonaws.com/monlam.ai.website/OCR/input/1717734852871-IMG_7580.jpeg"
       buffer=await get_buffer(image_url)
       try:
        coordinates = await google_ocr(buffer)
        text_data = get_text(coordinates)
        return {
            "success": True,
            "output": text_data,
            "responseTime": False,
        }
    
       except Exception as e:
        raise HTTPException(status_code=500, detail=f"ocr failed: {str(e)}")

@router.post("/")
async def ocr(request: Input, client_request: Request):
       token = request.id_token
       user_id = get_user_id(token)
       client_ip, source_app = get_client_metadata(client_request)
       db = next(get_db())
       try:
        image_url=request.input
        image=await get_buffer(image_url)
        coordinates = await google_ocr(image)
        text_data= get_text(coordinates)
        print(text_data)
        
        save_ocr_data(db, request.input, text_data, False, client_ip, source_app, user_id)

        return {
            "success": True,
            "output": text_data,
            "coordinates":coordinates,
            "responseTime": False,
         }
       except Exception as e:
        raise HTTPException(status_code=500, detail=f"ocr failed: {str(e)}")


def save_ocr_data(db, input_text, file_url, response_time, client_ip, source_app, user_id):
    ocr_data = {
        "input": input_text,
        "output": file_url,
        "response_time": response_time,
        "ip_address": client_ip,
        "version": None,
        "source_app": source_app,
        "user_id": user_id,
    }
    create_ocr(db, ocr_data)