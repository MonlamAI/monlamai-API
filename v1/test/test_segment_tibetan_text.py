import unittest
from v1.libs.segment_tibetan_text import segment_tibetan_text, TextSegment, SegmentedText
# Assuming TextSegment, SegmentedText, and segment_tibetan_text are imported from the module

class TestTextSegment(unittest.TestCase):

    def test_text_segment_initialization(self):
        segment = TextSegment(0, "Hello")
        self.assertEqual(segment.start, 0)
        self.assertEqual(segment.text, "Hello")


class TestSegmentedText(unittest.TestCase):

    def test_segmented_text_initialization(self):
        segments = [
            TextSegment(0, "Hello"),
            TextSegment(5, "World")
        ]
        segmented_text = SegmentedText(segments)
        self.assertEqual(len(segmented_text.segments), 2)
        self.assertEqual(segmented_text.segments[0].text, "Hello")
        self.assertEqual(segmented_text.segments[1].text, "World")

    def test_segmented_text_str(self):
        segments = [
            TextSegment(0, "Hello"),
            TextSegment(5, "World")
        ]
        segmented_text = SegmentedText(segments)
        expected_str = "Start: 0, Text: 'Hello'\nStart: 5, Text: 'World'"
        self.assertEqual(str(segmented_text), expected_str)


class TestSegmentTibetanText(unittest.TestCase):

    def test_segment_tibetan_text_basic(self):
        text = "བོད་། བོད་།"
        segmented = segment_tibetan_text(text)
        expected_segments = [
            TextSegment(0, "བོད"),
            TextSegment(3, "་"),
            TextSegment(4, "།"),
            TextSegment(5, " "),
            TextSegment(6, "་"),
            TextSegment(7, "།")
        ]
        
        for i, segment in enumerate(segmented.segments):
            self.assertEqual(segment.start, expected_segments[i].start)
            self.assertEqual(segment.text, expected_segments[i].text)

    def test_segment_tibetan_text_with_topic_breaker(self):
        text = "བོད་།། མི་།"
        segmented = segment_tibetan_text(text)
        expected_segments = [
            TextSegment(0, "བོད"),
            TextSegment(3, "་"),
            TextSegment(4, "།།"),
            TextSegment(6, " "),
            TextSegment(7, "་"),
            TextSegment(8, "།")
        ]
        
        for i, segment in enumerate(segmented.segments):
            self.assertEqual(segment.start, expected_segments[i].start)
            self.assertEqual(segment.text, expected_segments[i].text)

    def test_segment_tibetan_text_with_newline(self):
        text = "བོད་\nམི་"
        segmented = segment_tibetan_text(text)
        expected_segments = [
            TextSegment(0, "བོད"),
            TextSegment(3, "་"),
            TextSegment(4, ""),
            TextSegment(4, "མི"),
            TextSegment(6, "་"),
            TextSegment(7, ""),

        ]
        
        for i, segment in enumerate(segmented.segments):
            self.assertEqual(segment.start, expected_segments[i].start)
            self.assertEqual(segment.text, expected_segments[i].text)

if __name__ == "__main__":
    unittest.main()
