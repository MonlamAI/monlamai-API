from fastapi import Request, HTTPException

def get_id_token(request: Request) -> str:
    id_token = request.cookies.get("id_token")
    if id_token:
        return id_token
    return None
