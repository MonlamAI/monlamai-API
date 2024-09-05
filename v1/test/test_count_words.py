import pytest
import re
from v1.utils.get_translation_from_file import count_words  # Replace `your_module` with the actual module name where `count_words` is defined

# Test cases
@pytest.mark.parametrize("input_text, expected_count", [
    ("Hello world", 2),  # Simple case with two English words
    ("Hello", 1),  # Single word
    ("Hello world!", 2),  # Two words with punctuation
    ("", 0),  # Empty string
    # ("།བཀྲ་ཤིས། བདེ་ལེགས།", 2),  # Tibetan text with two words
    # ("།བཀྲ་ཤིས།", 1),  # Tibetan text with one word
    # ("Mixed text བཀྲ་ཤིས། English", 3),  # Mixed Tibetan and English text
    ("Hello123 world456", 2),  # Words with numbers
    ("123 456", 2),  # Only numbers, should be counted as words
    # ("Special characters !@#$%^&*()_", 0),  # Special characters only
])

def test_count_words(input_text, expected_count):
    assert count_words(input_text) == expected_count
