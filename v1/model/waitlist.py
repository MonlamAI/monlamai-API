
from v1.Config.Connection import db,prisma_connection

async def get_user_by_email(email: str):
    # Manually retrieve the session object
        user = await db.waitlist.find_unique(
               where={'email': email}
                )
        return user

async def create_waitlist(user_data: dict):
    user = await get_user_by_email(user_data['email'])
    
    if not user:
        data = {
            'name': user_data['name'],
            'email': user_data['email'],
        }

        user = await db.waitlist.create(data=data)
    
    return user