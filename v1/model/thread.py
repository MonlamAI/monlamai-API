from v1.Config.Connection import db,prisma_connection
from v1.model.user import get_user_by_email
async def create_thread(data: dict):
    thread = await db.thread.create(data=data)
    return thread


async def get_thread_by_id(thread_id: int):
    thread = await db.thread.find_unique(
        where={"id": thread_id},
        include={"chats": {"orderBy": {"createdAt": "asc"}}}
    )
    return thread



async def get_threads(user_email: str, limit: int = 10, offset: int = 0):
    user = await get_user_by_email(user_email)
    user_id = user.id
    threads = await db.thread.find_many(
        where={"createdById": user_id},
        include={"chats": True},
        order={"createdAt": "desc"},
        skip=offset,   # This is the offset parameter for pagination
        take=limit     # This is the limit parameter for pagination
    )
    
    return threads



async def delete_thread_by_id(thread_id: int):
    # Mock implementation - Replace with actual database call
    # Example: await db.execute(query)
    threads = await db.thread.update(
        where={"id":thread_id},
        data={"show":False}
    )
    return threads

async def update_is_completed(thread_id: int):
    # Mock implementation - Replace with actual database call
    # Example: await db.execute(query)
    threads = await db.thread.update(
        where={"id":thread_id},
        data={"is_completed":True}
    )
    return threads