def detect_language(text: str) -> str:
    """
    Detect the language of the given text based on its Unicode characters.
    Returns:
      - 'bo' for Tibetan
      - 'en' for English (default)
      - 'zh' for Chinese
      - 'fr' for French
      - 'unknown' if no known language is detected
    
    :param text: The text whose language needs to be detected.
    :return: The language code of the detected language.
    """
    if not text:
        raise ValueError("The provided text is empty.")

    # Initialize counts for each language
    language_counts = {'bo': 0, 'en': 0, 'zh': 0, 'fr': 0}
    
    # Unicode ranges for different languages
    tibetan_range = (0x0F00, 0x0FFF)
    chinese_range = (0x4E00, 0x9FFF)
    french_range = (0x00C0, 0x00FF)  # Extended Latin for French

    # Check each character in the text
    for char in text:
        code_point = ord(char)
        
        # Tibetan Unicode range
        if tibetan_range[0] <= code_point <= tibetan_range[1]:
            language_counts['bo'] += 1

        # Chinese Unicode range
        elif chinese_range[0] <= code_point <= chinese_range[1]:
            language_counts['zh'] += 1

        # French Unicode range
        elif french_range[0] <= code_point <= french_range[1]:
            language_counts['fr'] += 1

        # English (Basic Latin) is implicitly handled by default

    # Determine the language with the highest count
    detected_language = max(language_counts, key=language_counts.get)

    # Return the detected language or default to 'en'
    return detected_language if language_counts[detected_language] > 0 else 'en'
    
if __name__ == "__main__":
        re=detect_language('ཁམས་བཟང་། ཁམས་བཟང་།')
        print(re)