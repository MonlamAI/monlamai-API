from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import os

security = HTTPBearer()

SECRET_KEY = os.getenv("ACCESS_TOKEN_SECRET")  # Get your secret key from environment variables
ALGORITHM = "HS256"  # The algorithm used for encoding/decoding the JWT
API_TOKEN =os.getenv("API_KEY")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    
    if token != API_TOKEN:
        # If the token does not match the expected API token, raise a 401 Unauthorized error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True