import unittest
import asyncio  # <-- Add this import
from unittest.mock import patch
from jwt import ExpiredSignatureError
from v1.auth.token_verify import verify_and_parse_token, get_public_key, verify
import pytest

class TestJWTVerification(unittest.TestCase):

    @patch('v1.auth.token_verify.create_user')
    @patch('v1.auth.token_verify.verify_and_parse_token')
    @pytest.mark.asyncio
    async def test_verify(self, mock_verify_and_parse_token, mock_create_user):
        # Setup valid token and mocked response
        token = "valid_token"
        mock_verify_and_parse_token.return_value = {"sub": "user123"}
        mock_create_user.return_value = {"message": "User created", "user_id": "user123"}

        # Run the async test
        result = asyncio.run(verify(token))  # <-- Use asyncio.run()

        # Verify that create_user was called with the correct payload
        mock_create_user.assert_awaited_once_with({"sub": "user123"})
        self.assertEqual(result, {"message": "User created", "user_id": "user123"})

    @patch('v1.auth.token_verify.verify_and_parse_token', side_effect=ExpiredSignatureError)
    def test_verify_expired_token(self, mock_verify_and_parse_token):
        token = "expired_token"

        result = asyncio.run(verify(token))  # <-- Use asyncio.run()
        self.assertEqual(result, {"message": "token expired"})

    @patch('v1.auth.token_verify.verify_and_parse_token', side_effect=ValueError("Invalid token"))
    def test_verify_invalid_token(self, mock_verify_and_parse_token):
        token = "invalid_token"

        result = asyncio.run(verify(token))  # <-- Use asyncio.run()
        self.assertEqual(result, {"message": "Invalid token"})

