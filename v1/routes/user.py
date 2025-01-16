

from fastapi import  HTTPException, APIRouter,Request
from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
from v1.models import Gender
from v1.utils.utils import get_client_metadata
from v1.model.user import update_user,delete_user_by_email,create_user,get_user_by_email
from v1.utils.mixPanel_track import track_signup_input,track_user_input
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
    role: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    gender: Optional[str] = None
    interest: Optional[str] = None
    profession: Optional[str] = None
    birth_date: Optional[date] = None
    

@router.post("/create")
async def create_user_route(user_data: UserCreateSchema, client_request: Request):
    # Get client metadata
    # Attempt to create a new user in the database
    print('creating user')
    try:
        user_res = await create_user(user_data)
        userdb = user_res['user']
        print("creted user",userdb)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    client_ip, source_app, city, country = get_client_metadata(client_request)
  
    # Check if user creation was successful
    print("continueing",userdb)
    if not userdb or not userdb.id:
        raise HTTPException(status_code=400, detail="User creation failed")
    
    user = user_data.dict()
    # Populate the user data dictionary with additional metadata
    user.update({
        "id": userdb.id,
        "type": "registration",
        "source_app": source_app,
        "version": "0.0.1",
        "response_time": 0,
        "ip_address": client_ip,
        "city": city,
        "country": country,
        "name": userdb.username,
        "email": userdb.email
    })
    
    # Track the signup using the populated user data
    user['type']="registration" if user_res['created'] else "login"    
    track_signup_input(signup_data_dict=user,send_event=True, request=client_request)
    
    # Return a success response with the new user ID
    return {"message": "User created successfully", "user_id": userdb.id}



@router.post("/{email}/update")
async def update_user_route(email: str, user_data: UserUpdateSchema,client_request: Request):
    updated_user = await update_user(email, user_data.dict(exclude_unset=True))
    updated=updated_user.dict()
    updated['type']="update user"
    track_signup_input(signup_data_dict=updated,send_event=True, request=client_request)
    
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found or update failed")
    return {"message": "User updated successfully", "user": updated_user}

@router.get("/{email}")
async def get_user_route(email: str):
    user = await get_user_by_email(email)
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"user": user}

@router.delete("/{email}")
async def delete_user_route(email:str):
    user= await delete_user_by_email(email)
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {'deleted':True}