import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest

# Import your verify_token function
from v1.auth.auth_handler import verify_token

# Create a FastAPI app and add a protected route
app = FastAPI()

@app.get("/protected")
def protected_route(credentials: HTTPAuthorizationCredentials = Depends(verify_token)):
    return {"message": "Access granted"}

client = TestClient(app)

# Define test tokens and secrets
API_TOKEN = "qweqweqweqweqweqeqwe"
INVALID_API_TOKEN = "invalid_api_token"

@patch.dict(os.environ, {"API_KEY": API_TOKEN})
def test_verify_token_valid():
    # Test with a valid token
    response = client.get("/protected", headers={"Authorization": f"Bearer {API_TOKEN}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Access granted"}

@patch.dict(os.environ, {"API_KEY": API_TOKEN})
def test_verify_token_invalid():
    # Test with an invalid token
    response = client.get("/protected", headers={"Authorization": f"Bearer {INVALID_API_TOKEN}"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}

@patch.dict(os.environ, {"API_KEY": API_TOKEN})
def test_verify_token_missing():
    # Test with no token
    response = client.get("/protected")
    assert response.status_code == 403  # Update to 403 if FastAPI returns 403
    assert response.json() == {"detail": "Not authenticated"}  # Update to match the actual response
