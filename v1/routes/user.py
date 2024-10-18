

from fastapi import  HTTPException, APIRouter
from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
from v1.models import Gender
from v1.model.user import update_user,create_user,get_user_by_email

router = APIRouter()


class UserUpdateSchema(BaseModel):
    gender: Optional[Gender] = None
    country: Optional[str] = None
    city: Optional[str] = None
    birth_date: Optional[date] = None
    interest: Optional[str] = None
    profession: Optional[str] = None

class UserCreateSchema(BaseModel):
    email: EmailStr
    name: str
    picture: Optional[str] = None


@router.post("/create")
async def create_user_route(user_data: UserCreateSchema):
    user_id = await create_user(user_data.dict())
    if user_id is None:
        raise HTTPException(status_code=400, detail="User creation failed")
    return {"message": "User created successfully", "user_id": user_id}


@router.post("/{email}/update")
async def update_user_route(email: str, user_data: UserUpdateSchema):
    updated_user = await update_user(email, user_data.dict(exclude_unset=True))
    
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found or update failed")
    return {"message": "User updated successfully", "user": updated_user}

@router.get("/{email}")
async def get_user_route(email: str):
    user = await get_user_by_email(email)
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"user": user}