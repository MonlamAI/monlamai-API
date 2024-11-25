import os
from v1.model.user import create_user

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives import serialization

from fastapi import FastAPI, HTTPException
from jose import JWTError, jwt, ExpiredSignatureError
import requests
import base64

app = FastAPI()

# Replace with your Auth0 settings

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
API_IDENTIFIER = os.getenv("API_AUDIENCE")
ALGORITHMS = ["RS256"]  # Auth0 uses RS256 algorithm

# Get the Auth0 public keys for verification
def get_jwk():
    url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# Convert JWK to RSA public key
def get_public_key(jwk):
    # Extract modulus and exponent
    n = base64.urlsafe_b64decode(jwk['n'] + '==')  # Add padding to make it valid base64
    e = base64.urlsafe_b64decode(jwk['e'] + '==')  # Add padding to make it valid base64

    # Convert to integers
    n_int = int.from_bytes(n, byteorder='big')
    e_int = int.from_bytes(e, byteorder='big')

    # Create RSA public key object
    rsa_public_key = rsa.RSAPublicNumbers(e_int, n_int).public_key()

    return rsa_public_key

# Verify the token
def verify_id_token(id_token: str):
    try:
        # Get the JWKs to find the correct public key
        jwks = get_jwk()
        
        # Decode the token header to get the kid (key id)
        unverified_header = jwt.get_unverified_header(id_token)
        if unverified_header is None or "kid" not in unverified_header:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Find the key based on kid
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = key
                break
        
        if not rsa_key:
            raise HTTPException(status_code=401, detail="Unable to find appropriate key")
        
        # Get the RSA public key
        public_key = get_public_key(rsa_key)
        
        # Verify the JWT using the RSA public key
        payload = jwt.decode(id_token, public_key, algorithms=ALGORITHMS, audience=API_IDENTIFIER)
        
        # Return the decoded payload (user info from the token)
        return payload
    except ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError as e:
        print(e)
        raise HTTPException(status_code=401, detail="Token verification failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
async def verify(token):
    try:  
      payload=verify_id_token(token)
      if payload:
        data=await create_user(payload)
        return data['user'].id
    except ExpiredSignatureError:
        return {"message": "token expired"}
    except ValueError as e:
        return {"message": str(e)}