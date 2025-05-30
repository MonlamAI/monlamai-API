import numpy as np
from typing import List, Dict, Tuple

def get_bounding_box(annotation: Dict) -> Tuple[float, float, float, float]:
    vertices = annotation['boundingPoly']['vertices']
    x_coords = [v.get('x', 0) for v in vertices]
    y_coords = [v.get('y', 0) for v in vertices]
    return (min(x_coords), min(y_coords), max(x_coords), max(y_coords))

def distance(box1: Tuple[float, float, float, float], box2: Tuple[float, float, float, float]) -> float:
    def center(box):
        return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)
    
    c1 = center(box1)
    c2 = center(box2)
    return np.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)

def group_text_annotations(annotations: List[Dict], max_distance: float = 50) -> List[List[Dict]]:
    if not annotations:
        return []

    groups = []
    used_annotations = set()

    for i, annotation in enumerate(annotations):
        if i in used_annotations:
            continue

        current_group = [annotation]
        used_annotations.add(i)
        box = get_bounding_box(annotation)

        for j, other_annotation in enumerate(annotations[i+1:], start=i+1):
            if j in used_annotations:
                continue

            other_box = get_bounding_box(other_annotation)
            if distance(box, other_box) <= max_distance:
                current_group.append(other_annotation)
                used_annotations.add(j)

        groups.append(current_group)

    return groups

def process_text_annotations(text_annotations: List[Dict]) -> List[Dict]:
    grouped_annotations = group_text_annotations(text_annotations)
    
    result = []
    for group in grouped_annotations:
        text = ' '.join(annotation['description'] for annotation in group)
        bounding_boxes = [get_bounding_box(annotation) for annotation in group]
        x_min = min(box[0] for box in bounding_boxes)
        y_min = min(box[1] for box in bounding_boxes)
        x_max = max(box[2] for box in bounding_boxes)
        y_max = max(box[3] for box in bounding_boxes)
        
        result.append({
            'text': text,
            'boundingBox': {
                'vertices': [
                    {'x': x_min, 'y': y_min},
                    {'x': x_max, 'y': y_min},
                    {'x': x_max, 'y': y_max},
                    {'x': x_min, 'y': y_max}
                ]
            }
        })
    
    return result