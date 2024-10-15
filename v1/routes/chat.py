from fastapi import APIRouter, HTTPException, Request, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime
from v1.utils.utils import get_user_id, get_client_metadata
from v1.model.thread import create_thread, get_thread_by_id, get_threads
from v1.model.chat import create_chat,update_chat_output,fetch_chat_history,update_chat,get_chat_by_id
from v1.utils.chat_fetcher import get_ai_response
from v1.utils.get_id_token import get_id_token

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
    thread_id: Optional[int] = Field(None, description="ID of the thread to add the chat to")

class ChatOutput(BaseModel):
    id: int
    input: str
    output: str
    threadId: int
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
    thread_id: int
    chat: ChatOutput
    ai_response: str

# Endpoints

@router.post("/", response_model=ChatResponse)
async def chat(
    chat_input: CreateChatInput,
    client_request: Request
):
    """
    Handle chat messages. Create a new thread if `thread_id` is not provided.
    Otherwise, add the chat to the existing thread.
    """
    token = get_id_token(client_request)
    user_id = await get_user_id(token)
    # client_ip, source_app, city, country = get_client_metadata(client_request)
    
    try:
        # Determine whether to create a new thread or use existing
        if chat_input.thread_id:
            thread = await get_thread_by_id(chat_input.thread_id)
            if not thread:
                raise HTTPException(status_code=404, detail="Thread not found")
            thread_id = thread.id
        else:
            # Create a new thread
            new_thread_data = {
                "title": "New Chat Thread",  # You might want to customize the title
                "createdById": user_id
            }
            new_thread = await create_thread(new_thread_data)
            thread_id = new_thread.id
        
        # Prepare chat data
        chat_data = {
            "input": chat_input.input,
            "output": "",  # Placeholder, will be filled after AI response
            "threadId": thread_id,
            "senderId": user_id,
            "model": "default_model",  # Replace with actual model if applicable
            "latency": "0ms",          # Replace with actual latency measurement
            "token": "default_token",  # Replace with actual token if applicable
            # Add additional fields if necessary
        }
        
        # Create chat entry in the database
        new_chat = await create_chat(chat_data)
        
        # Fetch chat history for AI response
        chat_history = await fetch_chat_history(thread_id)
        
        # Get AI response
        ai_response = get_ai_response(chat_input.input, chat_history)
        
        # Update chat with AI response
        new_chat.output = ai_response
        updated_chat = await update_chat_output(new_chat.id, ai_response)
        
        # Optionally, you can add AI's response as a separate chat entry
        # depending on your application logic
        
        return ChatResponse(
            thread_id=thread_id,
            chat=updated_chat,
            ai_response=ai_response
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@router.put("/{chat_id}", response_model=ChatOutput)
async def update_existing_chat(
    chat_id: int,
    update: UpdateChatInput,
    client_request: Request
):
    """
    Update an existing chat message by performing actions like edit, like, or dislike.
    """
    token = get_id_token(client_request)
    user_id = await get_user_id(token)
    
    try:
        # Verify the chat exists
        chat = await get_chat_by_id(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        if chat.senderId != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this chat")
        
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

@router.get("/thread/{thread_id}", response_model=ThreadOutput)
async def get_thread(thread_id: int):
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

@router.get("/threads", response_model=List[ThreadOutput])
async def list_threads():
    """
    Retrieve all threads.
    """
    try:
        threads = await get_threads()
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

# chat_history = [
#          {"role": "human", "content": "Hello, I'm having trouble with my order."},
#          {"role": "ai", "content": "I'm sorry to hear that. Can you please provide me with your order number?"},
#          {"role": "human", "content": "My order number is #12345."},
#          {"role": "ai", "content": "Thank you for providing your order number. I've looked it up and I see that your order is currently in transit. Is there a specific issue you're experiencing?"},
#          {"role": "human", "content": "The tracking hasn't updated in 3 days."},
#          {"role": "ai", "content": "I understand your concern. Sometimes tracking information can be delayed. Let me check the status with our shipping partner. Can you please wait a moment?"},
#         ]