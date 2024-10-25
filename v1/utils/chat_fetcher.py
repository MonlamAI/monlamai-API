from dotenv import load_dotenv
import os
import json
import requests
import httpx
from fastapi.responses import StreamingResponse
load_dotenv(override=True)
import re
import asyncio
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
    body = {
        'user_input': user_input,
        'chat_history': json.dumps(chat_history)  # Serialize list to JSON string
    }

    # Headers
   
    
    try:
        # Make the POST request with empty data
        response = requests.post(url, json=body, headers=headers, data='')

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




async def chat_stream(text: str, history=[], on_complete=None,cancel_event={}):
    print(text)
    # Retrieve environment variables
    url = os.getenv("LLM_MODEL_URL")
    url = f"{url}/generate_stream"

    # Define the event stream generator
    async def event_stream():
        generated_text = None
        final_text = ''
                
        metadata = None
        buffer = ''  # Initialize buffer for partial data

        try:
            body = {
                "user_input": text,
                "chat_history": json.dumps(history)  # Ensure history is passed as a JSON string
            }
            headers = {
            'Accept': 'application/json'
            }
            async with httpx.AsyncClient() as client:
                async with client.stream("POST", url, json=body, headers=headers) as response:
                    try:
                        async for chunk in response.aiter_text():
                            print(chunk)
                            if cancel_event.is_set():  # Check if the cancel event is triggered
                                
                               raise asyncio.CancelledError("Stream canceled by user.")
                            # Accumulate chunks in the buffer
                            buffer += chunk
                            # Process all complete lines in the buffer
                            while '\n' in buffer:
                                line, buffer = buffer.split('\n', 1)
                                line = line.strip()
                                if not line:
                                    continue

                                if line.startswith("data:"):
                                    json_data = line[len("data:"):].strip()
                                    
                                    if not json_data:
                                        continue

                                    try:
                                        # For debugging: Limit the length of printed data
                                        # print("Received json_data:", json_data[:500])
                                        parsed_data = json.loads(json_data)
                                    except json.JSONDecodeError as e:
                                        # The JSON data is incomplete; wait for more data
                                        buffer2 = line + '\n' + buffer  # Re-add the line to buffer
                                        print('buffer', buffer2)
                                        
                                        break  # Exit the loop to read more data

                                    text_value = parsed_data.get("text")
                                    if text_value:
                                        final_text += text_value
                                        yield f"data: {json.dumps({'text': text_value})}\n\n"
                                    
                                    generated_text = parsed_data.get("generated_text")
                                    metadata = parsed_data.get("metadata",{})
                                    valid = parsed_data.get("response",True) 
                                    
                                    
                                    if generated_text:
                                        yield f"data: {json.dumps({'generated_text': generated_text, 'metadata': metadata,'valid':valid})}\n\n"
                                        return
                    except asyncio.CancelledError as e:
                        metadata={
                                "model":"",
                                "latency":0,
                                "tokens":0
                                }
                        yield f"data: {json.dumps({'generated_text': final_text, 'metadata': metadata,'valid':True})}\n\n"
                        return
        except Exception as e:
            yield f"event: error\ndata: Stream error: {str(e)}\n\n"
            

        finally:
            # Ensure on_complete is called even if an error occurs
            if on_complete:
                generated_text = generated_text or final_text
                asyncio.create_task(on_complete(generated_text or '', metadata ))

    return StreamingResponse(event_stream(), media_type="text/event-stream;charset=UTF-8;")
