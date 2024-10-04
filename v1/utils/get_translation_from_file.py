
import ijson
import re
from v1.libs.segment_tibetan_text import segment_tibetan_text 
def count_words(text: str, isTibetan: bool) -> int:
    if isTibetan:
        # Tibetan word count (example regex, adjust as per actual Tibetan word structure)
        segmented_text = segment_tibetan_text(text)
        return len(segmented_text.segments)
    else:
        # English word count
        words = re.findall(r'\b\w+\b', text)
        return len(words)



def get_translation_from_file(search_key: str, direction: str) -> str:
    # Path to your dictionary file
    DICTIONARY_FILE_PATH = (
        'v1/dict-data/en_bo_translations.json' if direction == 'bo' else 'v1/dict-data/bo_en_translations.json'
    )
    try:
        # Split the search_key into individual words
        words = search_key.split()
        # Create a mapping of lowercase search words to their original forms
        words_lower_to_original = {word.lower(): word for word in words}
        words_set = set(words_lower_to_original.keys())  # For faster lookup

        # Dictionary to hold translations for the words we need
        translations = {}

        # Open the file for incremental parsing
        with open(DICTIONARY_FILE_PATH, 'r', encoding='utf-8') as file:
            # Initialize the parser
            parser = ijson.parse(file)
            current_key = None
            for prefix, event, value in parser:
                if event == 'map_key':
                    current_key = value
                    # Convert the key to lowercase for case-insensitive matching
                    key_lower = current_key.lower()
                elif event == 'string' and current_key:
                    if key_lower in words_set:
                        # Store the translation using the original search word
                        original_search_word = words_lower_to_original[key_lower]
                        translations[original_search_word] = value
                        # Remove the word from the set since we found its translation
                        words_set.remove(key_lower)
                        # If all words have been found, break early
                        if not words_set:
                            break
                    current_key = None  # Reset for the next key-value pair
                else:
                    current_key = None  # Ensure current_key is reset if event is not 'string'

        # Get the translation for each word in the original order
        translated_words = [translations.get(word, "") for word in words]
        # Join the translated words with spaces
        return ' '.join(translated_words)

    except Exception as e:
        print(f"Error processing JSON file: {e}")
        return ''