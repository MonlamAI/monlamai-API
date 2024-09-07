def chunk_tibetan_text(text, chunk_size=200):
    chunks = []
    current_index = 0

    while current_index < len(text):
        next_index = current_index + chunk_size

        # If next_index is beyond the length of the text, adjust it to the text length
        if next_index >= len(text):
            next_index = len(text)
        else:
            # Find the nearest ། or space character before or at next_index
            last_delimiter = max(
                text.rfind("།", current_index, next_index),
                text.rfind(" ", current_index, next_index)
            )
            if last_delimiter < current_index:
                # If no delimiter is found after the current_index, use the chunk_size
                last_delimiter = next_index
            else:
                last_delimiter += 1  # Include the delimiter in the chunk
            next_index = last_delimiter

        chunks.append(text[current_index:next_index].strip())
        current_index = next_index

    return chunks
