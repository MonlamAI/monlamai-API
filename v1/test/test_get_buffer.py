import pytest
import asynctest
from v1.libs.get_buffer import get_buffer

@pytest.mark.asyncio
async def test_get_buffer():
    # Define the URL and the expected content
    test_url = "https://s3.ap-south-1.amazonaws.com/monlam.ai.website/STT/input/1719051360666-undefined"
    expected_content = b"audio data"

    # Mock the AsyncClient's get method
    with asynctest.patch("httpx.AsyncClient.get", return_value=asynctest.CoroutineMock(status_code=200, content=expected_content)) as mock_get:
        # Call the function
        result = await get_buffer(test_url)

        # Assert that the result is as expected
        assert result == expected_content
        # Ensure the GET request was made to the correct URL
        mock_get.assert_awaited_once_with(test_url)
