from fastapi import APIRouter, HTTPException,Query
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from v1.utils.utils import get_client_metadata
from v1.model.thread import create_thread, get_thread_by_id, get_threads, delete_thread_by_id,get_total_threads_count
from v1.model.chat import create_chat, update_chat_output, fetch_chat_history, update_chat, get_chat_by_id
from v1.utils.chat_fetcher import chat, chat_stream
from v1.model.user import get_user_by_email
import json
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
cancellation_events = {}
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
            return await handle_existing_chat(chat_input,chat_input.thread_id)

        # Create or fetch thread
        thread_id = await get_or_create_thread(chat_input.thread_id, chat_input.input, user_id)
        
        # Fetch chat history and get AI response
        chat_history = await fetch_chat_history(thread_id)
      
        ai_response = await get_ai_response(chat_input.input, chat_history, chat_input.thread_id,user_id)

        return ai_response

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

# Helper Functions

async def handle_existing_chat(chat_input: CreateChatInput,thread_id):
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
            await update_chat(existing_chat.id, updated_chat_data,metadata)

    cancel_event = asyncio.Event()
    cancellation_events[thread_id] = cancel_event
    stream = await chat_stream(chat_input.input, chat_history, on_complete,cancel_event)
    return stream

async def get_or_create_thread(thread_id: str, input_text: str, user_id: int):
    if thread_id:
        thread = await get_thread_by_id(thread_id)
        if not thread:
            thread = await create_thread({"id": thread_id, "title": input_text, "createdById": user_id})
    else:
        thread = await create_thread({"title": input_text, "createdById": user_id})
    
    return thread.id

async def create_new_chat(input_text: str, thread_id: str, user_id: int,upload_data):
    token=upload_data.get('metadata').get('tokens')
    chat_data = {
        "input": input_text,
        "output": upload_data.get('generated_text'),  # Placeholder for AI response
        "threadId": thread_id,
        "senderId": user_id,
        "model": upload_data.get('metadata').get('model'),  # Replace with actual model if applicable
        "latency": upload_data.get('metadata').get('latency'),  # Replace with actual latency measurement
        "token":     json.dumps(token)
,  # Replace with actual token if applicable
    }
    output=await create_chat(chat_data)
    return output

async def get_ai_response(input_text: str, chat_history, thread_id:str,user_id):
    async def on_complete(generated_text, metadata):
        if generated_text:
            upload_data={}
            upload_data['metadata'] = metadata
            upload_data['generated_text']=generated_text
            asyncio.create_task(create_new_chat(input_text,thread_id,user_id,upload_data))


    cancel_event = asyncio.Event()
    cancellation_events[thread_id] = cancel_event
    stream=await chat_stream(input_text, chat_history, on_complete,cancel_event)
    return stream





@router.post("/cancel/{thread_id}")
async def cancel_stream(thread_id: str):
    """
    Endpoint to cancel the stream for a specific thread.
    """
    if thread_id in cancellation_events:
        cancellation_events[thread_id].set()  # Trigger the cancellation event
        return {"message": f"Stream for thread {thread_id} canceled"}
    else:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")



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

# @router.get("/threads/{user_email}")
# async def list_threads(user_email: str):
#     """
#     Retrieve all threads.
#     """
#     try:
#         threads = await get_threads(user_email)
#         return threads
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Fetching threads failed: {str(e)}")

class PaginationRequest(BaseModel):
    page: int = 1  # Default to page 1
    limit: int = 10  # Default limit to 10 items per page

@router.post("/threads/{user_email}")
async def list_threads_post(user_email: str, pagination: PaginationRequest):
    """
    Retrieve paginated threads using page number and limit provided in the body.
    
    - **page**: The page number.
    - **limit**: Number of threads to retrieve per page.
    """
    try:
        # Calculate the offset based on the page number and limit
        offset = (pagination.page - 1) * pagination.limit
        user = await get_user_by_email(user_email)
        if not user:
            print(user)
            raise HTTPException(status_code=404, detail="User not found")
        user_id = user.id
        threads = await get_threads(user_id, limit=pagination.limit, offset=offset)
        total= await get_total_threads_count(user_id)
        return {
            "page": pagination.page,
            "limit": pagination.limit,
            "threads": threads,
            "count":total
        }
        
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
