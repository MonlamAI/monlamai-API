from v1.Config.Connection import db
from fastapi import HTTPException
from pydantic import ValidationError
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

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


class UserCreateSchema(BaseModel):
    email: EmailStr
    name: str
    picture: Optional[str] = None
    role: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    gender: Optional[str] = None
    interest: Optional[str] = None
    profession: Optional[str] = None
    birth_date: Optional[date] = None


async def create_user(user_data: UserCreateSchema):
    try:
        # Check if user already exists
        user = await get_user_by_email(user_data.email)
        if user:
            return {'user': user, 'created': False}

        # Prepare the data to create a new user
        data = {
            'username': user_data.name,
            'email': user_data.email,
            'picture': user_data.picture,
        }

        optional_fields = ['gender', 'city', 'country', 'interest', 'profession', 'birth_date']
        for field in optional_fields:
            value = getattr(user_data, field, None)
            if value:
                data[field] = value

        # Create the new user
        user = await db.user.create(data=data)
        return {'user': user, 'created': True}

    except ValidationError as ve:
        # Handle validation errors for user_data
        raise HTTPException(status_code=422, detail=f"Validation Error: {ve.errors()}")

    except db.exceptions.UniqueConstraintViolation as ucve:
        # Handle database unique constraint violations
        raise HTTPException(status_code=409, detail=f"User with the given email already exists.")

    except db.exceptions.DatabaseError as de:
        # Handle general database errors
        raise HTTPException(status_code=500, detail="An error occurred while accessing the database. Please try again later.")

    except Exception as e:
        # Handle unexpected exceptions
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


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