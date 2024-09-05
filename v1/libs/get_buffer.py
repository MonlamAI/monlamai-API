import httpx


async def get_buffer(url: str) -> bytes:
    """Fetch audio from a URL and return it as a buffer (byte array)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()  # Ensure the request was successful
        # Return the content of the response as bytes
        return response.content