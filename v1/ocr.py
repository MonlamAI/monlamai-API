from fastapi import APIRouter, HTTPException
from v1.utils.google_ocr import google_ocr
from v1.libs.url_to_buffer import get_buffer
from pydantic import BaseModel
import httpx
from v1.libs.get_text import get_text
import json

router = APIRouter()

class Input(BaseModel):
    input: str
    


@router.get("/")
def read_root():
    return {"message": "Welcome to API v1 OCR"}

@router.get("/check")
async def check():
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
async def ocr_text(request:Input):
       try:
        image_url=request.input
        image=await get_buffer(image_url)
        coordinates = await google_ocr(image)
        text_data= get_text(coordinates)
        
        return {
            "success": True,
            "output": text_data,
            "coordinates":coordinates,
            "responseTime": False,
         }
       except Exception as e:
        raise HTTPException(status_code=500, detail=f"ocr failed: {str(e)}")
