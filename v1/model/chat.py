from v1.Config.Connection import db,prisma_connection
from v1.model.thread import get_thread_by_id
import json

async def create_chat(data: dict):
    chat = await db.chat.create(data=data)
    return chat

import json

async def update_chat(chat_id: int, data: dict, metadata: dict = None):
    update_data = {}
    action = data.get("action")
    edit_text = data.get("edit_input")
    edit_response = data.get("edit_output")

    if action == "like":
        update_data["liked_count"] = {"increment": 1}
    elif action == "dislike":
        update_data["disliked_count"] = {"increment": 1}
    elif action == "edit" and edit_text:
        update_data["edit_input"] = edit_text
        update_data["edit_output"] = edit_response

    if metadata:
        update_data["latency"] = metadata.get('latency')
        update_data["model"] = metadata.get('model')
        # Stringify the 'tokens' object and save it
        update_data["token"] = json.dumps(metadata.get('tokens', {}))

    if not update_data:
        return None

    chat = await db.chat.update(
        where={"id": chat_id},
        data=update_data
    )
    return chat


async def get_chat_by_id(chat_id: int):   
    chat = await db.chat.find_unique(
        where={"id": chat_id}
    )
    return chat

async def update_chat_output(chat_id: int, output: str,metadata: dict):
    update_data = {"output": output}
    if metadata:
        update_data["latency"] = metadata['latency']
        update_data["model"]= metadata['model']
        update_data["token"]= metadata['tokens']
 
    
    updated_chat = await db.chat.update(
        where={"id": chat_id},
        data=update_data
    )
    return updated_chat

async def fetch_chat_history(thread_id: str):
    """
    Fetch chat history for a given thread to provide context for AI responses.
    """
    thread = await get_thread_by_id(thread_id)
    if not thread:
        return []
    
    chat_history = []
    for chat in thread.chats:
        role = "user" if chat.senderId == thread.createdById else "system"
        chat_history.append({"role": role, "content": chat.input})
        if chat.output:
            chat_history.append({"role": 'system', "content": chat.output})
    
    return chat_history