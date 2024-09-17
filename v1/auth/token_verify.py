from jose import jwt, JWTError
import requests
import os
from v1.model.user import create_user
from jwt import ExpiredSignatureError, InvalidTokenError, DecodeError


def get_public_key(auth0_domain: str, kid: str) -> dict:
  
    jwks_url = f"https://{auth0_domain}/.well-known/jwks.json"
    response = requests.get(jwks_url)
    jwks = response.json()

    for key in jwks['keys']:
        if key['kid'] == kid:
            return {
                "kty": key['kty'],
                "kid": key['kid'],
                "use": key['use'],
                "n": key['n'],
                "e": key['e']
            }

    raise ValueError("Unable to find the appropriate key.")

def verify_and_parse_token(token: str) -> dict:
    AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
    API_AUDIENCE = os.getenv("API_AUDIENCE")
    try:
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = get_public_key(AUTH0_DOMAIN, unverified_header['kid'])

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        ) 
        return payload
    
    except ExpiredSignatureError:
        raise ValueError("Token has expired")
    
    except InvalidTokenError:
        raise ValueError("Invalid token")

    except Exception as e:
        raise ValueError(f"An error occurred while verifying the token: {str(e)}")


    
async def verify(token):
    try:  
      payload=verify_and_parse_token(token)
      if payload:
        data=await create_user(payload)
        return data
    except ExpiredSignatureError:
        return {"message": "token expired"}
    except ValueError as e:
        return {"message": str(e)}