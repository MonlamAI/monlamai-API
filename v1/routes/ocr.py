from fastapi import APIRouter, HTTPException,Request,Query
from v1.utils.google_ocr import google_ocr
from v1.libs.get_buffer import get_buffer
from pydantic import BaseModel
from v1.libs.get_text import get_text
from typing import Optional
from v1.utils.utils import get_user_id
from v1.utils.utils import get_client_metadata
from v1.model.edit_inference import edit_inference
from v1.model.create_inference import create_ocr
from PIL import Image
from io import BytesIO
from v1.libs.ocr_parse import process_text_annotations
import asyncio
router = APIRouter()

class Input(BaseModel):
    input: str
    id_token:Optional[str] = None


@router.get("/")
async def check_ocr():
       image_url ="https://s3.ap-south-1.amazonaws.com/monlam.ai.website/OCR/input/1717734852871-IMG_7580.jpeg"
       buffer=await get_buffer(image_url)
       image = Image.open(BytesIO(buffer))
       width, height = image.size
       try:
        coordinates = await google_ocr(buffer)
        text_data = get_text(coordinates)
        parse_coordinates=process_text_annotations(coordinates['textAnnotations'])
        return {
            "success": True,
            "output": text_data,
            "responseTime": False,
            "coordinates":parse_coordinates,
            "height":height,
            "width":width
        }
    
       except Exception as e:
        raise HTTPException(status_code=500, detail=f"ocr failed: {str(e)}")

@router.post("/")
async def ocr(request: Input, client_request: Request):
       token = request.id_token
       user_id =await get_user_id(token)
       client_ip, source_app,city,country = get_client_metadata(client_request)
       try:
        image_url=request.input
        buffer=await get_buffer(image_url)
        image = Image.open(BytesIO(buffer))
        width, height = image.size
        coordinates = await google_ocr(buffer)
        text= get_text(coordinates)
        parse_coordinates=process_text_annotations(coordinates['textAnnotations'])

        ocr_data = {
        "input": request.input,
        "output": text,
        "response_time": 0,
        "ip_address": client_ip,
        "version": None,
        "source_app": source_app,
        "user_id": user_id,
        "city": city,
        "country": country,
         }
        data= await create_ocr(ocr_data)
        
        return {
            "id":data.id,
            "success": True,
            "output": text,
            "coordinates":parse_coordinates,
            "height":height,
            "width":width
         }
        
       except Exception as e:
        raise HTTPException(status_code=500, detail="ocr failed from server")




@router.put("/{id}")
async def update_ocr(id: int, action: str = Query(..., description="Action to perform: 'edit', 'like', or 'dislike'"), edit_text: str = None):
    # Validate the action type
    if action == 'edit' and not edit_text:
        raise HTTPException(status_code=400, detail="Edit text must be provided for 'edit' action.")

    # Call the edit_inference function to update the record in ocr table
    updated_record = await edit_inference('ocr', id, action, edit_text)

    if not updated_record:
        raise HTTPException(status_code=404, detail="Record not found")

    return {"message": f"Record {action}d successfully", "data": updated_record}



