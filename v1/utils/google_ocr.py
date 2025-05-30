import json
from google.cloud import vision
from google.oauth2 import service_account
from google.protobuf.json_format import MessageToJson
from google.cloud.vision import AnnotateImageResponse
import os
import io
from PIL import Image
def is_png(image_data):
    return image_data[:8] == b'\x89PNG\r\n\x1a\n'


async def read_file_async(image_path):
    with open(image_path, 'rb') as image_file:
        return image_file.read()
    

async def google_ocr(image, lang_hint=None):
    environment = os.getenv('ENV', 'development')
    # Load credentials
    credentials_path = '/etc/secrets/ocr_credentials.json' if environment == 'production' else 'env/ocr_credentials.json'
    
    credentials = service_account.Credentials.from_service_account_file(credentials_path)

    client = vision.ImageAnnotatorClient(credentials=credentials)

    # Check if the image is a file path or already in bytes
    if isinstance(image, str):
        content = await read_file_async(image)
    elif isinstance(image, Image.Image):
        # Convert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        content = img_byte_arr.getvalue()
    else:
        content = image
    # Prepare the image content for the request
    ocr_image = vision.Image(content=content)
    image_context = {"language_hints": [lang_hint]} if lang_hint else {}
    # Prepare the request
    features = [
        {
            "type_": vision.Feature.Type.DOCUMENT_TEXT_DETECTION,
            "model": "builtin/weekly",
        }
    ]
    

    try:
        # Perform the OCR request
        response = client.annotate_image({"image": ocr_image, "features": features, "image_context": image_context})
        # Convert the response to JSON using MessageToJson
        response_json = AnnotateImageResponse.to_json(response)
        return json.loads(response_json)

    except Exception as e:
        print(f"Failed to perform OCR: {str(e)}")
        raise RuntimeError("Failed to perform OCR")
