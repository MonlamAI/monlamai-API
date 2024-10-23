from v1.Config.Connection import db,prisma_connection
from datetime import datetime, timezone
async def get_user_by_email(email: str):
    # Manually retrieve the session object
        user = await db.user.find_unique(
               where={'email': email}
                )
        return user
async def get_user_by_id(id: int):
    # Manually retrieve the session object
        user = await db.user.find_unique(
               where={'id': id}
                )
        return user  


async def create_user(user_data: dict):
    user = await get_user_by_email(user_data['email'])
    
    if not user:
        data = {
            'username': user_data['name'],
            'email': user_data['email'],
            'picture': user_data.get('picture'),
        }

        # Conditionally add fields if they exist in user_data
        optional_fields = ['gender', 'city', 'country', 'interest', 'profession','birth_date']
        
        for field in optional_fields:
            if field in user_data:
                data[field] = user_data[field]
        
        user = await db.user.create(data=data)
    
    return user


async def delete_user_by_email(email: str):
        user = await db.user.delete(
               where={'email': email}
                )
        return user


async def update_user(email: str, user_data: dict):
    user = await get_user_by_email(email)
    if not user:
        return None

    # Filter out None values to avoid overwriting with null
    update_data = {k: v for k, v in user_data.items() if v is not None}
    # Convert birth_date to a full ISO 8601 DateTime if it's only a date

    if 'birth_date' in update_data:
        date_obj = datetime.strptime(str(update_data['birth_date']), "%Y-%m-%d").replace(hour=0, minute=0, second=0)
        utc_date_obj = date_obj.replace(tzinfo=timezone.utc)
        update_data['birth_date'] = utc_date_obj
    # Conditionally update only if there's data to update
    if update_data:
        updated_user = await db.user.update(
            where={'email': email},
            data=update_data
        )
        return updated_user

    return user 