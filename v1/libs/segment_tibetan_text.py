class TextSegment:
    def __init__(self, start, text):
        self.start = start
        self.text = text

class SegmentedText:
    def __init__(self, segments):
        self.segments = segments

    def __str__(self):
        return "\n".join(f"Start: {segment.start}, Text: '{segment.text}'" for segment in self.segments)

def segment_tibetan_text(text: str) -> SegmentedText:
    dot = "་"
    breaker = "། །"
    topic_breaker = "།།"
    symbol = "༄༄༅༅།"
    space = " "
    new_line = "\n"
    return_segment = "\r"
    current_start = 0
    segments = []

    text_split_data = text.split(dot)
    text_split_data = [l + "_་" for l in text_split_data]
    text_split_data = [segment for sublist in (s.split("_") for s in text_split_data) for segment in sublist]
    text_split_data = text_split_data[:-1]  # Remove last empty element

    for index, segment in enumerate(text_split_data):
        if new_line in segment:
            split_array_with_new_line = segment.split(new_line)
            split_array_with_new_line = [l.replace(return_segment, "") for l in split_array_with_new_line]
            for l in split_array_with_new_line:
                new_segment = TextSegment(current_start, l)
                segments.append(new_segment)
                current_start += len(l)

        elif breaker in segment:
            split_word = segment.split(breaker)
            if len(split_word) > 2:
                split_word[2] = split_word[1]
                split_word[1] = breaker

            if topic_breaker in split_word[0]:
                new_split = split_word[0].split(topic_breaker)
                if len(new_split) > 1:
                    new_split[2] = new_split[1]
                    new_split[1] = topic_breaker
                    for l in new_split:
                        new_segment = TextSegment(current_start, l)
                        segments.append(new_segment)
                        current_start += len(l)
                split_word.pop(0)

            for l in split_word:
                new_segment = TextSegment(current_start, l)
                segments.append(new_segment)
                current_start += len(l)

        elif space in segment:
            segment_array = segment.split(space)
            if len(segment_array) > 1:
                if symbol in segment_array[1]:
                    segment_array[1] = " །"
                    if len(segment_array) > 2:
                        segment_array.append(segment_array[2])
                else:
                    segment_array[1] = " "
                    if len(segment_array) > 2:
                        segment_array.append(segment_array[2])

            for index, word in enumerate(segment_array):
                current_segment = word.replace(symbol, "") if index == 2 else word
                new_segment = TextSegment(current_start, current_segment)
                segments.append(new_segment)
                current_start += len(current_segment)

        elif topic_breaker in segment:
            split_word = segment.split(topic_breaker)
            if len(split_word) > 0:
                for l in split_word:
                    new_segment = TextSegment(current_start, l)
                    segments.append(new_segment)
                    current_start += len(l)

        else:
            new_segment = TextSegment(current_start, segment)
            segments.append(new_segment)
            current_start += len(segment)

    return SegmentedText(segments)