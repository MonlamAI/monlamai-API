from v1.Config.Connection import db,prisma_connection

async def create_thread(data: dict):
    thread = await db.thread.create(data=data)
    return thread


async def get_thread_by_id(thread_id: int):
    thread = await db.thread.find_unique(
        where={"id": thread_id},
        include={"chats": True}
    )
    return thread

async def get_threads():
    threads = await db.thread.find_many(
        include={"chats": True}
    )
    return threads