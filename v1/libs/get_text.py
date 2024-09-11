from openpecha.formatters.ocr.google_vision import GoogleVisionFormatter
from openpecha.formatters.ocr.ocr import OCRFormatter, BBox, UNICODE_CHARCAT_FOR_WIDTH
from pathlib import Path
import statistics
from fontTools import unicodedata
import sys
import json
from typing import Dict, Any, Optional, List, Tuple

formatter = OCRFormatter()
remove_non_character_lines = True
remove_rotated_boxes = True


# Define types for clarity
OCRObject = Dict[str, Any]
BBoxList = List[BBox]

def has_space_attached(symbol):
    # Check if 'property' exists in symbol and it is not None
    if ('property' in symbol and symbol['property'] is not None and
            'detectedBreak' in symbol['property'] and
            'type' in symbol['property']['detectedBreak'] and
            symbol['property']['detectedBreak']['type'] == "SPACE"):
        return True


def dict_to_bbox(word):
    confidence = word.get('confidence')
    if 'boundingBox' not in word or 'vertices' not in word['boundingBox']:
        return None
    vertices = word['boundingBox']['vertices']
    bboxinfo = GoogleVisionFormatter.get_bboxinfo_from_vertices(vertices)
    if bboxinfo == None:
        return None
    if remove_rotated_boxes and bboxinfo[4] > 0:
        return None
    return BBox(bboxinfo[0], bboxinfo[1], bboxinfo[2], bboxinfo[3], bboxinfo[4], 
        confidence=confidence)

def get_char_base_bboxes_and_avg_width(response):
    bboxes = []
    widths = []
    if 'fullTextAnnotation' not in response:
        return None, None
    for page in response['fullTextAnnotation']['pages']:
        for block in page['blocks']:
            for paragraph in block['paragraphs']:
                for word in paragraph['words']:
                    bbox = dict_to_bbox(word)
                    if bbox is None:
                        continue
                    cur_word = ""
                    for symbol in word['symbols']:
                        symbolunicat = unicodedata.category(symbol['text'][0])
                        if symbolunicat in UNICODE_CHARCAT_FOR_WIDTH:
                            vertices = symbol['boundingBox']['vertices']
                            width = GoogleVisionFormatter.get_width_of_vertices(vertices)
                            if width is not None and width > 0:
                                widths.append(width)
                        cur_word += symbol['text']
                        if has_space_attached(symbol):
                            cur_word += " "
                    if cur_word:
                        bbox.text = cur_word
                        bbox.language = formatter.get_main_language_code(cur_word)
                        bboxes.append(bbox)
    avg_width = statistics.mean(widths) if widths else None
    return bboxes, avg_width


def build_page(bboxes, avg_char_width):
    text_with_coordinates = []  # To store the text along with their coordinates
    text = ""
    if not bboxes:
        return text,text_with_coordinates
    sorted_bboxes = formatter.sort_bboxes(bboxes)
    bbox_lines = formatter.get_bbox_lines(sorted_bboxes)
    for bbox_line in bbox_lines:
        if remove_non_character_lines and not formatter.bbox_line_has_characters(bbox_line):
            continue
        if avg_char_width:
            bbox_line = formatter.insert_space_bbox(bbox_line, avg_char_width)
        for bbox in bbox_line:
            text += bbox.text
            coordinates = (bbox.x1, bbox.y1, bbox.x2, bbox.y2)
            
            text_with_coordinates.append((text, coordinates))
        text += "\n"
        text_with_coordinates.append(("\n", None)) 
    text += "\n"
    return text,text_with_coordinates

def get_text(ocr_object: OCRObject) -> Optional[str]:
    bboxes, avg_width = get_char_base_bboxes_and_avg_width(response=ocr_object)
    if bboxes is None:
        return None
     # A list to hold the text and coordinates
   
    text,text_with_coordinates = build_page(bboxes, avg_width)
    print(text_with_coordinates)
    return text



if __name__ == '__main__':
    print('started')
    with open('v1/ocr_sample.json', 'r', encoding='utf-8') as file:
        ocr_data = json.load(file)  # Load JSON data from the file
    result_text = get_text(ocr_data)
    print(result_text)