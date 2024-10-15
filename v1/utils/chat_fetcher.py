from dotenv import load_dotenv
import json
load_dotenv(override=True)


def converse(user_input,history):
    
    body={
        "input": user_input,
        "history": history}
    json_mylist = json.dumps(body, separators=(',', ':'))
    return json_mylist

def get_ai_response(user_input,history):
    # Predict the AI's response based on the user input
    response = converse(user_input,history)
    
    return response
