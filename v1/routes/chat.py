from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from v1.utils.utils import get_client_metadata
from v1.model.thread import create_thread, get_thread_by_id, get_threads, delete_thread_by_id
from v1.model.chat import create_chat, update_chat_output, fetch_chat_history, update_chat, get_chat_by_id
from v1.utils.chat_fetcher import chat, chat_stream
from v1.model.user import get_user_by_email
import asyncio

router = APIRouter(tags=["chat"])

# Pydantic Models

class CreateThreadInput(BaseModel):
    title: str

class ThreadOutput(BaseModel):
    id: int
    title: str
    createdById: int
    createdAt: datetime
    updatedAt: datetime

class CreateChatInput(BaseModel):
    input: str
    user: str
    thread_id: Optional[str] = Field(None, description="ID of the thread to add the chat to")
    chat_id: Optional[int] = Field(None, description="ID of the chat to update")

class ChatOutput(BaseModel):
    id: int
    input: str
    output: str
    threadId: str
    senderId: int
    createdAt: datetime
    updatedAt: datetime
    liked_count: int
    disliked_count: int
    model: str
    latency: str
    token: str
    edit_input: Optional[str] = None
    edit_output: Optional[str] = None

class UpdateChatInput(BaseModel):
    action: str = Field(..., description="Action to perform: 'edit', 'like', or 'dislike'")
    edit_text: Optional[str] = Field(None, description="Text to replace input/output when editing")

class ChatHistoryItem(BaseModel):
    role: str
    content: str

class ChatResponse(BaseModel):
    thread_id: str
    chat: ChatOutput
    ai_response: str

# Endpoints

@router.post("/")
async def chat_response(chat_input: CreateChatInput):
    """
    Handle chat messages. Create a new thread if `thread_id` is not provided.
    Otherwise, add the chat to the existing thread.
    """
    user = await get_user_by_email(chat_input.user)
    user_id = user.id

    try:
        # Check if updating an existing chat
        if chat_input.chat_id:
            existing_chat = await get_chat_by_id(chat_input.chat_id)
            if not existing_chat:
                raise HTTPException(status_code=404, detail="Chat not found")

            chat_history = await fetch_chat_history(existing_chat.threadId)

            async def on_complete(generated_text, metadata):
                if generated_text:
                    updated_chat_data = {
                        "edit_input": chat_input.input,
                        "edit_output": generated_text,
                        "action": "edit"
                    }
                    asyncio.create_task(update_chat_output(existing_chat.id, updated_chat_data))

            # Get AI response
            ai_response = await chat_stream(chat_input.input, chat_history, on_complete)
            return ai_response

        # Determine whether to create a new thread or use existing
        if chat_input.thread_id:
            thread = await get_thread_by_id(chat_input.thread_id)
            if not thread:
                thread = await create_thread({"id": chat_input.thread_id, "title": chat_input.input, "createdById": user_id})
            thread_id = thread.id
        else:
            # Create a new thread if no thread_id provided
            thread = await create_thread({"title": chat_input.input, "createdById": user_id})
            thread_id = thread.id

        # Prepare chat data
        chat_data = {
            "input": chat_input.input,
            "output": "",  # Placeholder, will be filled after AI response
            "threadId": thread_id,
            "senderId": user_id,
            "model": "default_model",  # Replace with actual model if applicable
            "latency": 0,  # Replace with actual latency measurement
            "token": 23,  # Replace with actual token if applicable
        }

        # Create chat entry in the database
        new_chat = await create_chat(chat_data)

        # Fetch chat history for AI response
        chat_history = await fetch_chat_history(thread_id)

        async def on_complete(generated_text, metadata):
            if generated_text:
                asyncio.create_task(update_chat_output(new_chat.id, generated_text))

        # Get AI response
        ai_response = await chat_stream(chat_input.input, chat_history, on_complete)
        return ai_response

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@router.put("/{chat_id}")
async def update_existing_chat(chat_id: int, update: UpdateChatInput):
    """
    Update an existing chat message by performing actions like edit, like, or dislike.
    """
    try:
        # Verify the chat exists
        chat = await get_chat_by_id(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        update_data = {
            "action": update.action,
            "edit_text": update.edit_text
        }

        updated_chat = await update_chat(chat_id, update_data)
        if not updated_chat:
            raise HTTPException(status_code=400, detail="Failed to update chat")

        return updated_chat
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Updating chat failed: {str(e)}")

@router.get("/thread/{thread_id}")
async def get_thread(thread_id: str):
    """
    Retrieve a specific thread by ID.
    """
    try:
        thread = await get_thread_by_id(thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        return thread
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fetching thread failed: {str(e)}")

@router.delete("/thread/{thread_id}")
async def delete_thread(thread_id: str):
    """
    Delete a specific thread by ID.
    """
    try:
        success = await delete_thread_by_id(thread_id)
        if not success:
            raise HTTPException(status_code=404, detail="Thread not found")
        return {"message": "Thread deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deleting thread failed: {str(e)}")

@router.get("/threads/{user_email}")
async def list_threads(user_email: str):
    """
    Retrieve all threads.
    """
    try:
        threads = await get_threads(user_email)
        return threads
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fetching threads failed: {str(e)}")

@router.get("/{chat_id}", response_model=ChatOutput)
async def get_chat(chat_id: int):
    """
    Retrieve a specific chat by ID.
    """
    try:
        chat = await get_chat_by_id(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        return chat
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fetching chat failed: {str(e)}")
