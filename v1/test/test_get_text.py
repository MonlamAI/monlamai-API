
import pytest
from unittest.mock import patch, MagicMock
from openpecha.formatters.ocr.ocr import OCRFormatter, BBox
from v1.libs.get_text import get_text


# Sample mock data
mock_ocr_data = {
    'fullTextAnnotation': {
        'pages': [
            {
                'blocks': [
                    {
                        'paragraphs': [
                            {
                                'words': [
                                    {
                                        'confidence': 0.95,
                                        'boundingBox': {
                                            'vertices': [
                                                {'x': 10, 'y': 10},
                                                {'x': 20, 'y': 10},
                                                {'x': 20, 'y': 20},
                                                {'x': 10, 'y': 20}
                                            ]
                                        },
                                        'symbols': [
                                            {'text': 'H', 'boundingBox': {'vertices': [{'x': 10, 'y': 10}, {'x': 15, 'y': 10}, {'x': 15, 'y': 20}, {'x': 10, 'y': 20}]}},
                                            {'text': 'i', 'boundingBox': {'vertices': [{'x': 15, 'y': 10}, {'x': 20, 'y': 10}, {'x': 20, 'y': 20}, {'x': 15, 'y': 20}]}},
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
}

# Mocking external methods if needed
@patch('openpecha.formatters.ocr.google_vision.GoogleVisionFormatter.get_bboxinfo_from_vertices')
@patch('openpecha.formatters.ocr.google_vision.GoogleVisionFormatter.get_width_of_vertices')
@patch('openpecha.formatters.ocr.ocr.OCRFormatter.sort_bboxes')
@patch('openpecha.formatters.ocr.ocr.OCRFormatter.get_bbox_lines')
@patch('openpecha.formatters.ocr.ocr.OCRFormatter.bbox_line_has_characters')
@patch('openpecha.formatters.ocr.ocr.OCRFormatter.insert_space_bbox')
def test_get_text(mock_insert_space_bbox, mock_bbox_line_has_characters, mock_get_bbox_lines, mock_sort_bboxes, mock_get_width_of_vertices, mock_get_bboxinfo_from_vertices):

    # Setup mocks
    mock_get_bboxinfo_from_vertices.return_value = [10, 10, 20, 20, 0]
    mock_get_width_of_vertices.return_value = 5
    mock_sort_bboxes.return_value = [[BBox(10, 10, 20, 20, 0, text="Hi")]]
    mock_get_bbox_lines.return_value = [[BBox(10, 10, 20, 20, 0, text="Hi")]]
    mock_bbox_line_has_characters.return_value = True
    mock_insert_space_bbox.return_value = [BBox(10, 10, 20, 20, 0, text="Hi")]

    result_text = get_text(mock_ocr_data)
    
    assert result_text == "Hi\n\n"
