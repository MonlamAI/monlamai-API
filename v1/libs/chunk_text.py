def is_tibetan(text):
    # Expanded Tibetan Unicode ranges
    tibetan_ranges = [
        (0x0F00, 0x0FFF),  # Tibetan script
        (0x0F00, 0x0F47),  # Basic characters
        (0x0F49, 0x0F6C),  # Letters
        (0x0F71, 0x0F97),  # Vowel signs and modifiers
        (0x0F99, 0x0FBC),  # Subjoined letters
        (0x0FD0, 0x0FD4),  # Symbols
    ]
    
    return any(
        any(start <= ord(char) <= end for start, end in tibetan_ranges)
        for char in text
        if char.strip()
    )

def chunk_tibetan_text(text, max_chunk_size=200):
    if not is_tibetan(text):
        words = text.split()
        return [" ".join(words[i:i + 150]) for i in range(0, len(words), 150)]
    
    # Tibetan text delimiters in priority order
    primary_delimiters = ['།།', '།', '༎', '༏', '༐', '༑']
    secondary_delimiters = ['་', ' ']
    
    def find_best_split_point(segment, target_size):
        # First try primary delimiters
        for delimiter in primary_delimiters:
            last_pos = segment[:target_size + len(delimiter)].rfind(delimiter)
            if last_pos > 0:
                return last_pos + len(delimiter)
        
        # If no primary delimiter found, try secondary delimiters
        for delimiter in secondary_delimiters:
            last_pos = segment[:target_size + len(delimiter)].rfind(delimiter)
            if last_pos > 0:
                return last_pos + len(delimiter)
        
        # If no delimiter found, ensure we don't split in the middle of a syllable
        if target_size >= len(segment):
            return len(segment)
        
        # Look for a safe position to split (after a tsek or space)
        for i in range(target_size, max(0, target_size - 20), -1):
            if i < len(segment) and any(segment[i-1] == delim for delim in ['་', ' ']):
                return i
        
        # If no safe split point found, use the target size
        return min(target_size, len(segment))

    def normalize_chunk(chunk):
        # Remove leading/trailing spaces and unnecessary delimiters
        chunk = chunk.strip()
        for delimiter in primary_delimiters + secondary_delimiters:
            if chunk.startswith(delimiter):
                chunk = chunk[len(delimiter):].strip()
        return chunk

    chunks = []
    current_pos = 0
    text = text.strip()
    
    while current_pos < len(text):
        # Determine next chunk size
        remaining_text = text[current_pos:]
        target_size = min(max_chunk_size, len(remaining_text))
        
        # Find the best split point
        split_point = find_best_split_point(remaining_text, target_size)
        
        # Extract and normalize the chunk
        chunk = normalize_chunk(remaining_text[:split_point])
        
        # Only add non-empty chunks
        if chunk:
            chunks.append(chunk)
        
        # Move to next position
        current_pos += split_point
        
        # Skip any delimiters at the current position
        while current_pos < len(text) and any(text[current_pos:].startswith(d) for d in primary_delimiters + secondary_delimiters):
            current_pos += 1
    
    # Post-process chunks to ensure proper endings
    processed_chunks = []
    for i, chunk in enumerate(chunks):
        # Add shad if chunk doesn't end with a proper delimiter and isn't the last chunk
        if i < len(chunks) - 1 and not any(chunk.endswith(d) for d in primary_delimiters):
            if chunk.endswith('་'):
                chunk = chunk[:-1] + '།'
            else:
                chunk = chunk + '།'
        processed_chunks.append(chunk)
    
    return processed_chunks