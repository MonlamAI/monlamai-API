import json
from google.cloud import vision
from google.oauth2 import service_account
from google.protobuf.json_format import MessageToJson
from google.cloud.vision import AnnotateImageResponse


def is_png(image_data):
    return image_data[:8] == b'\x89PNG\r\n\x1a\n'


async def read_file_async(image_path):
    with open(image_path, 'rb') as image_file:
        return image_file.read()
    

async def google_ocr(image, lang_hint=None):
    # Load credentials
    credentials = service_account.Credentials.from_service_account_file('env/ocr_credentials.json')

    client = vision.ImageAnnotatorClient(credentials=credentials)

    # Check if the image is a file path or already in bytes
    if isinstance(image, str):
        content = await read_file_async(image)
    else:
        content = image
    
    # Prepare the image content for the request
    ocr_image = vision.Image(content=content)
    image_context = {}
    if lang_hint:
        image_context["language_hints"] = [lang_hint]
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
        response = json.loads(response_json)
        return response

    except Exception as e:
        print("Failed to perform OCR:", e)
        raise e
