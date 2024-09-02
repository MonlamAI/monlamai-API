from fastapi import APIRouter, HTTPException
from v1.utils.google_ocr import google_ocr
from v1.libs.url_to_buffer import get_buffer
from pydantic import BaseModel
import httpx

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
        text_data = await google_ocr(buffer)
        return {
            "success": True,
            "ocr_data": text_data,
            "responseTime": False,
        }
    
       except Exception as e:
        raise HTTPException(status_code=500, detail=f"ocr failed: {str(e)}")

@router.post("/")
async def get_text(request:Input):
       try:
        image_url=request.input
        image=await get_buffer(image_url)
        text_data = await google_ocr(image)
        return {
            "success": True,
            "ocr_data": text_data,
            "responseTime": False,
         }
       except Exception as e:
        raise HTTPException(status_code=500, detail=f"ocr failed: {str(e)}")
