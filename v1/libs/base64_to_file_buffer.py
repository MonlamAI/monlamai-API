import base64
import io

def base64_to_file_buffer(base64_string: str) -> io.BytesIO:
    # Decode the Base64 string to binary data
    file_data = base64.b64decode(base64_string)
    
    # Create a BytesIO object from the binary data
    file_buffer = io.BytesIO(file_data)
    
    return file_buffer

