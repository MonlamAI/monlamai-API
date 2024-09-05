from v1.libs.base64_to_file_buffer import base64_to_file_buffer  
import base64
import io
import pytest

def test_base64_to_file_buffer_valid():
    original_data = b"This is a test."
    base64_string = base64.b64encode(original_data).decode('utf-8')
    result = base64_to_file_buffer(base64_string)
    assert isinstance(result, io.BytesIO)
    assert result.getvalue() == original_data

def test_base64_to_file_buffer_invalid():
    invalid_base64_string = "!!!not_base64!!!"
    with pytest.raises(ValueError, match="Input string is not a valid Base64 encoded string"):
        base64_to_file_buffer(invalid_base64_string)

def test_base64_to_file_buffer_none():
    with pytest.raises(ValueError, match="Input base64 string is empty, None, or only whitespace"):
        base64_to_file_buffer(None)

def test_base64_to_file_buffer_empty_string():
    with pytest.raises(ValueError, match="Input base64 string is empty, None, or only whitespace"):
        base64_to_file_buffer("")

def test_base64_to_file_buffer_whitespace_string():
    with pytest.raises(ValueError, match="Input base64 string is empty, None, or only whitespace"):
        base64_to_file_buffer("   ")
