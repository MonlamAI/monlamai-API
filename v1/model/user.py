from v1.Config.Connection import db,prisma_connection

async def get_user_by_email(email: str):
    # Manually retrieve the session object
        user = await db.user.find_unique(
               where={'email': email}
                )
        return user
   

async def create_user(user_data: dict):
        user =await get_user_by_email(user_data['email'])
        if not user:
            user = await db.user.create(
            {'email': user_data['email'],
             'username': user_data['name'],
             'picture': user_data['picture']
             }
             )
        return user.id
