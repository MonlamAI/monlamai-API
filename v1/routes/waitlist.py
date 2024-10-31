from fastapi import  HTTPException, APIRouter
from pydantic import BaseModel, EmailStr
from v1.model.waitlist import create_waitlist

router = APIRouter()
class UserCreateSchema(BaseModel):
    email: EmailStr
    name: str



@router.post("/create")
async def create_wait_list(user_data: UserCreateSchema):
    user_id = await create_waitlist(user_data.dict())
    if user_id is None:
        raise HTTPException(status_code=400, detail="User creation failed")
    return {"message": "User created successfully", "user_id": user_id}