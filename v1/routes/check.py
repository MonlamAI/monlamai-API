from fastapi import APIRouter, HTTPException, Request, Query
from v1.utils.translator import (
    translator_llm,
    translator_mt,
)

from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address

# Load environment variables
load_dotenv()

# Configuration constants
MAX_CONCURRENT_REQUESTS = 5
CHUNK_MAX_SIZE = 50
VERSION = "1.0.0"

# Setup router and rate limiter
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.get("/", status_code=200)
async def check_translation(client_request: Request):
    """
    Health check endpoint for translation service

    Args:
        client_request (Request): Client request object

    Returns:
        dict: Translation check result
    """
    text = "hi hello how are you"
    direction = "bo"

    try:
        # Try getting translation from MT
        try:
            mt_response = await translator_mt(text, direction)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"MT service has issues: {str(e)}")

        # Try getting translation from LLM
        try:
            llm_response = await translator_llm(text, direction)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM service has issues: {str(e)}")

        # Combine and return results with status 200
        return {
            "status": "success",
            "translation": mt_response['translation'] + llm_response['translation'],
            "responseTime": mt_response['responseTime'] + llm_response.get('responseTime', 0),
        }

    except HTTPException as http_exc:
        # Re-raise HTTP exceptions
        raise http_exc

    except Exception as e:
        # Catch-all for any unexpected issues
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")
