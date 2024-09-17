
import ijson
import re

def count_words(text: str, isTibetan: bool) -> int:
    if isTibetan:
        # Tibetan word count (example regex, adjust as per actual Tibetan word structure)
        words = re.findall(r'[\u0F00-\u0FFF]+', text)
    else:
        # English word count
        words = re.findall(r'\b\w+\b', text)
    return len(words)


def get_translation_from_file(search_key: str, direction:str) -> str:
    # Path to your dictionary file
    DICTIONARY_FILE_PATH = 'v1/dict-data/en-bo_dictionary.json' if direction=='bo' else 'v1/dict-data/bo-en_dictionary.json'
    try:
        # Open the file for streaming
        with open(DICTIONARY_FILE_PATH, 'r', encoding='utf-8') as file:
            # Use ijson to parse the file incrementally
            parser = ijson.parse(file)
            
            # Create a dictionary to hold the translations
            translations = {}
            current_key = None
            
            # Iterate through the JSON tokens
            for prefix, event, value in parser:
                if event == 'map_key':
                    current_key = value
                elif event == 'string' and current_key:
                    # Store the translation in the dictionary
                    translations[current_key] = value
                    current_key = None

         # Split the search_key into individual words
        words = search_key.split()
        # Get the translation for each word
        translated_words = [translations.get(word,"") for word in words]
        # Join the translated words with spaces
        return ' '.join(translated_words)    
    
    except Exception as e:
        print(f"Error processing JSON file: {e}")
        return ''
    
if __name__ == "__main__": 
         text="hi hello"
         direction='bo'
         data=get_translation_from_file(text,direction)
         print(data)