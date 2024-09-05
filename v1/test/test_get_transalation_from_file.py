import pytest
from v1.utils.get_translation_from_file import get_translation_from_file



def test_get_translation_en_to_bo():
    result = get_translation_from_file("recreation", "bo")
    assert result == "རྩེད་འཇོ།"

def test_get_translation_bo_to_en():
    result = get_translation_from_file("ཀ་ཅ།", "en")
    assert result == "thing"

def test_get_translation_with_missing_key():
    result = get_translation_from_file("sasasqsqs", "bo")
    assert result == ''