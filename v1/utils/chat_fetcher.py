from dotenv import load_dotenv
import os
import json
import requests
import httpx
from fastapi.responses import StreamingResponse
load_dotenv(override=True)

headers = {
        'Accept': 'application/json'
    }

def chat(user_input, chat_history=None):
    """
    Sends a POST request to the LLM API with the given user input and chat history.

    Parameters:
    - user_input (str): The message from the user.
    - chat_history (list, optional): The history of the chat as a list of messages. Defaults to an empty list.

    Returns:
    - dict: The JSON response from the API if successful.
    - str: An error message if the request fails or the response is invalid.
    """
    # Endpoint URL
    url = os.getenv("LLM_MODEL_URL")

    # Default chat_history to empty list if not provided
    if chat_history is None:
        chat_history = []

    # Prepare query parameters
    params = {
        'user_input': user_input,
        'chat_history': json.dumps(chat_history)  # Serialize list to JSON string
    }

    # Headers
   
    
    try:
        # Make the POST request with empty data
        response = requests.post(url, params=params, headers=headers, data='')

        # Raise an HTTPError if the response was unsuccessful
        response.raise_for_status()

        # Attempt to parse the JSON response
        data=response.json()
        return data['response']

    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err} - Response: {response.response}"
    except requests.exceptions.ConnectionError as conn_err:
        return f"Connection error occurred: {conn_err}"
    except requests.exceptions.Timeout as timeout_err:
        return f"Timeout error occurred: {timeout_err}"
    except requests.exceptions.RequestException as req_err:
        return f"An error occurred: {req_err}"
    except ValueError:
        return "Response content is not valid JSON."






async def chat_stream(text: str,history=[], on_complete=None):
    # Retrieve environment variables
    url = os.getenv("LLM_MODEL_URL") 
    url = f"{url}/generate_stream"
    
    # Define the event stream generator
    async def event_stream():
        try:
            params = {
                "user_input": text,
                "chat_history": json.dumps(history)  # Ensure history is passed as a JSON string
            }

            async with httpx.AsyncClient() as client:
                async with client.stream("POST", url, params=params, headers=headers) as response:
                    async for chunk in response.aiter_bytes():
                        # Process each chunk of data
                        data = chunk.decode('utf-8').strip()
                        if not data:
                            continue

                        for line in data.split('\n'):
                            if line.startswith("data:"):
                                json_data = line[len("data:"):].strip()
                                if not json_data:
                                    continue

                                parsed_data = json.loads(json_data)
                                text_value = parsed_data.get("text")
                                generated_text = parsed_data.get("generated_text")
                                metadata=parsed_data.get("metadata")
                                # latency = metadata["latency"]
                                # tokens = metadata["tokens"]
                                # model = metadata["model"]
                                
                                if text_value:
                                    yield f"data: {json.dumps({'text': text_value})}\n\n"

                                # Yield the generated text as an SSE event and end the stream
                                if generated_text:
                                    yield f"data: {json.dumps({'generated_text': generated_text,'metadata':metadata})}\n\n"
                                    return
        except Exception as e:
            yield f"event: error\ndata: Stream error: {str(e)}\n\n"
        
        finally:
            if on_complete:
                if generated_text and metadata:
                   await on_complete(generated_text or '',metadata )  # Use empty string if no generated_text


    return StreamingResponse(event_stream(), media_type="text/event-stream")
