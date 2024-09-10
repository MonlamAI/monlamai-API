import requests
from io import BytesIO
import os 

def check_quota():
    api_key=os.getenv("OPENAI_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    url = "https://api.openai.com/v1/usage"  # URL for usage check
    response = requests.get(url, headers=headers)
    usage_data = response.json()
    return usage_data

def get_audio_from_url(url):
  
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error downloading from URL: {e}")
        return None

def whisper_stt(audio_data):
    api_key=os.getenv("OPENAI_API_KEY")
    
    quota_data = check_quota()
    remaining_quota = quota_data.get('remaining_quota', 0)
    if remaining_quota <= 0:
        print("Quota exceeded. Please check your billing plan.")
        return None
    
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    # Handle URL
    if isinstance(audio_data, str) and audio_data.startswith('http'):
        audio_data = get_audio_from_url(audio_data)
        if audio_data is None:
            return None

    # Convert to BytesIO if audio_data is bytes
    if isinstance(audio_data, bytes):
        audio_buffer = BytesIO(audio_data)
    elif isinstance(audio_data, BytesIO):
        audio_buffer = audio_data
    else:
        raise ValueError("audio_data must be either bytes, BytesIO, or a public URL")

    
    audio_buffer.seek(0)
    
    # Read a sample of the audio data for debugging
    audio_buffer.seek(0)  # Reset the buffer position
    
    files = {
        "file": ("audio.mp3", audio_buffer, "audio/mpeg")
    }
    data = {
        "model": "whisper-1",
        "language": "en"
    }

    response = requests.post(url, headers=headers, files=files, data=data)
        
        # Debug: Print full response details
    response_data = response.json()
    print(response_data)
    response.raise_for_status()

    if response_data:
            if 'text' in response_data:
                text=response_data['text']
                return text
            elif 'error' in response_data:
                print(f"API Error: {response_data['error']}")
                return None
            else:
                print("Unexpected response format")
                return None
    else:
            print(f"Unexpected response content type: {response.headers.get('Content-Type')}")
            return None

  
