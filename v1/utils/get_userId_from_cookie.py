from fastapi import Request, HTTPException
from v1.model.user import get_user_by_email

async def get_user_id_from_cookie(request: Request) -> str:
    user_email = request.cookies.get("email")
    if user_email:
        user= await get_user_by_email(user_email)
        return user.id
    return None
