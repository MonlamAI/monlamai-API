from fastapi import APIRouter, HTTPException, Request
from v1.utils.translator import translator_llm, translator_mt

router = APIRouter()

@router.head("/", status_code=200)
async def check_translation(client_request: Request):

    try:
        # Try calling MT and LLM translation services for health check
        text = "i am llm model melong"
        direction = "bo"
        # Check if MT service is functioning
        try:
            await translator_mt(text, direction)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"MT service has issues: {str(e)}")

        # Check if LLM service is functioning
        try:
            await translator_llm(text, direction)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM service has issues: {str(e)}")

        # Return a success response with no body
        return None

    except HTTPException as http_exc:
        # Re-raise HTTP exceptions
        raise http_exc

    except Exception as e:
        # Catch-all for any unexpected issues
        raise HTTPException(status_code=500, detail=f"Translation service health check failed: {str(e)}")
