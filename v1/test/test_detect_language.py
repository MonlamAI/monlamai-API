from v1.utils.language_detect import detect_language
import pytest

# Test cases for detect_language function
@pytest.mark.parametrize("input_text, expected_language", [
    ("ཁམས་བཟང་། ཁམས་བཟང་།", 'bo'),  # Tibetan text
    ("Hello, how are you?", 'en'),  # English text
    ("你好，世界", 'zh'),  # Chinese text
    ("Mixed ཁམས་བཟང་། 你好", 'bo'),  # Mixed Tibetan and Chinese text, prioritize Tibetan
    ("No special characters", 'en'),  # Plain English text with no special characters
    ("", 'en'),  # Empty text (this will raise an error)
])
def test_detect_language(input_text, expected_language):
    if not input_text:  # Test case for empty string
        with pytest.raises(ValueError, match="The provided text is empty."):
            detect_language(input_text)
    else:
        assert detect_language(input_text) == expected_language