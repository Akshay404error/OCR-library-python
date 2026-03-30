"""
Utility functions for matocr8d
"""

import re
import logging
from typing import List, Dict, Any, Union

logger = logging.getLogger(__name__)


def confidence_score(results: List[Dict[str, Any]]) -> float:
    """
    Calculate average confidence score from OCR results
    
    Args:
        results: List of OCR result dictionaries
        
    Returns:
        Average confidence score (0.0 to 1.0)
    """
    if not results:
        return 0.0
    
    confidences = []
    for result in results:
        if isinstance(result, dict) and 'confidence' in result:
            confidences.append(result['confidence'])
    
    if not confidences:
        return 0.0
    
    return sum(confidences) / len(confidences)


def text_cleanup(text: str, 
                remove_extra_spaces: bool = True,
                remove_special_chars: bool = False,
                lowercase: bool = False) -> str:
    """
    Clean up extracted text
    
    Args:
        text: Input text to clean
        remove_extra_spaces: Whether to remove extra whitespace
        remove_special_chars: Whether to remove special characters
        lowercase: Whether to convert to lowercase
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    cleaned = text
    
    if remove_extra_spaces:
        # Remove extra spaces and newlines
        cleaned = re.sub(r'\s+', ' ', cleaned.strip())
    
    if remove_special_chars:
        # Keep only alphanumeric characters and basic punctuation
        cleaned = re.sub(r'[^a-zA-Z0-9\s.,!?;:]', '', cleaned)
    
    if lowercase:
        cleaned = cleaned.lower()
    
    return cleaned


def format_output(results: List[Dict[str, Any]], 
                 text_only: bool = False,
                 with_confidence: bool = False,
                 detailed: bool = False) -> Union[str, Dict[str, Any]]:
    """
    Format OCR results into desired output format
    
    Args:
        results: List of OCR result dictionaries
        text_only: Return only extracted text
        with_confidence: Include confidence scores
        detailed: Return detailed information
        
    Returns:
        Formatted output
    """
    if not results:
        if text_only:
            return ""
        elif detailed:
            return {"text": "", "results": [], "confidence": 0.0}
        else:
            return {"text": "", "confidence": 0.0}
    
    if text_only:
        # Combine all text
        text_parts = []
        for result in results:
            if isinstance(result, dict) and 'text' in result:
                text_parts.append(result['text'])
        return ' '.join(text_parts)
    
    elif detailed:
        # Return detailed results
        formatted_results = []
        total_confidence = 0.0
        conf_count = 0
        
        for result in results:
            if isinstance(result, dict):
                formatted_result = {
                    'text': result.get('text', ''),
                    'confidence': result.get('confidence', 0.0),
                    'bbox': result.get('bbox', {}),
                    'engine': result.get('engine', 'unknown')
                }
                formatted_results.append(formatted_result)
                
                if 'confidence' in result:
                    total_confidence += result['confidence']
                    conf_count += 1
        
        avg_confidence = total_confidence / conf_count if conf_count > 0 else 0.0
        
        return {
            'text': ' '.join([r['text'] for r in formatted_results if r['text']]),
            'results': formatted_results,
            'confidence': avg_confidence,
            'total_words': len(formatted_results)
        }
    
    else:
        # Return text with confidence
        text_parts = []
        total_confidence = 0.0
        conf_count = 0
        
        for result in results:
            if isinstance(result, dict):
                if 'text' in result:
                    text_parts.append(result['text'])
                if 'confidence' in result:
                    total_confidence += result['confidence']
                    conf_count += 1
        
        avg_confidence = total_confidence / conf_count if conf_count > 0 else 0.0
        
        output = {'text': ' '.join(text_parts)}
        
        if with_confidence:
            output['confidence'] = avg_confidence
        
        return output


def merge_overlapping_boxes(boxes: List[Dict[str, Any]], 
                           overlap_threshold: float = 0.5) -> List[Dict[str, Any]]:
    """
    Merge overlapping text boxes
    
    Args:
        boxes: List of text boxes with bounding boxes
        overlap_threshold: Minimum overlap ratio to merge boxes
        
    Returns:
        List of merged text boxes
    """
    if not boxes:
        return []
    
    def calculate_overlap(box1, box2):
        """Calculate overlap ratio between two boxes"""
        x1 = max(box1['x'], box2['x'])
        y1 = max(box1['y'], box2['y'])
        x2 = min(box1['x'] + box1['width'], box2['x'] + box2['width'])
        y2 = min(box1['y'] + box1['height'], box2['y'] + box2['height'])
        
        if x2 <= x1 or y2 <= y1:
            return 0.0
        
        overlap_area = (x2 - x1) * (y2 - y1)
        area1 = box1['width'] * box1['height']
        area2 = box2['width'] * box2['height']
        
        return overlap_area / min(area1, area2)
    
    merged = []
    used = set()
    
    for i, box1 in enumerate(boxes):
        if i in used:
            continue
            
        current_box = box1.copy()
        used.add(i)
        
        for j, box2 in enumerate(boxes[i+1:], i+1):
            if j in used:
                continue
                
            if calculate_overlap(current_box, box2) > overlap_threshold:
                # Merge boxes
                x = min(current_box['x'], box2['x'])
                y = min(current_box['y'], box2['y'])
                x2 = max(current_box['x'] + current_box['width'], 
                        box2['x'] + box2['width'])
                y2 = max(current_box['y'] + current_box['height'], 
                        box2['y'] + box2['height'])
                
                current_box = {
                    'x': x,
                    'y': y,
                    'width': x2 - x,
                    'height': y2 - y,
                    'text': current_box.get('text', '') + ' ' + box2.get('text', ''),
                    'confidence': (current_box.get('confidence', 0) + box2.get('confidence', 0)) / 2
                }
                used.add(j)
        
        merged.append(current_box)
    
    return merged


def validate_ocr_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate and filter OCR results
    
    Args:
        results: List of OCR result dictionaries
        
    Returns:
        List of validated results
    """
    validated = []
    
    for result in results:
        if not isinstance(result, dict):
            continue
        
        # Check required fields
        if 'text' not in result:
            continue
        
        text = result['text'].strip()
        if not text:
            continue
        
        # Validate confidence
        confidence = result.get('confidence', 0.0)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            confidence = 0.0
        
        # Validate bounding box
        bbox = result.get('bbox', {})
        if not isinstance(bbox, dict):
            bbox = {}
        
        validated_result = {
            'text': text,
            'confidence': confidence,
            'bbox': bbox,
            'engine': result.get('engine', 'unknown')
        }
        
        validated.append(validated_result)
    
    return validated
