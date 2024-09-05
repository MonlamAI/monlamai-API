import base64
import io

def base64_to_file_buffer(base64_string: str) -> io.BytesIO:
    if not base64_string or base64_string.strip() == "":
        raise ValueError("Input base64 string is empty, None, or only whitespace")
    
    try:
        # Decode the Base64 string to binary data
        file_data = base64.b64decode(base64_string)
    except base64.binascii.Error as e:
        # Handle the case where the input string is not valid Base64
        raise ValueError("Input string is not a valid Base64 encoded string") from e
    
    # Create a BytesIO object from the binary data
    file_buffer = io.BytesIO(file_data)
    
    return file_buffer
