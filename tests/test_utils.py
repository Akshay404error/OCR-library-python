"""
Tests for utility functions
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from matocr8d.utils import (
    confidence_score, text_cleanup, format_output, 
    merge_overlapping_boxes, validate_ocr_results
)


class TestUtils(unittest.TestCase):
    """Test cases for utility functions"""
    
    def test_confidence_score_empty(self):
        """Test confidence score with empty results"""
        score = confidence_score([])
        self.assertEqual(score, 0.0)
    
    def test_confidence_score_single(self):
        """Test confidence score with single result"""
        results = [{'confidence': 0.85}]
        score = confidence_score(results)
        self.assertEqual(score, 0.85)
    
    def test_confidence_score_multiple(self):
        """Test confidence score with multiple results"""
        results = [
            {'confidence': 0.90},
            {'confidence': 0.80},
            {'confidence': 0.70}
        ]
        score = confidence_score(results)
        self.assertEqual(score, 0.8)
    
    def test_confidence_score_no_confidence_field(self):
        """Test confidence score with results missing confidence field"""
        results = [{'text': 'hello'}, {'text': 'world'}]
        score = confidence_score(results)
        self.assertEqual(score, 0.0)
    
    def test_text_cleanup_basic(self):
        """Test basic text cleanup"""
        text = "  Hello   World  "
        cleaned = text_cleanup(text)
        self.assertEqual(cleaned, "Hello World")
    
    def test_text_cleanup_special_chars(self):
        """Test text cleanup with special characters"""
        text = "Hello @#$% World!"
        cleaned = text_cleanup(text, remove_special_chars=True)
        self.assertEqual(cleaned, "Hello World")
    
    def test_text_cleanup_lowercase(self):
        """Test text cleanup with lowercase conversion"""
        text = "HELLO WORLD"
        cleaned = text_cleanup(text, lowercase=True)
        self.assertEqual(cleaned, "hello world")
    
    def test_text_cleanup_empty(self):
        """Test text cleanup with empty string"""
        cleaned = text_cleanup("")
        self.assertEqual(cleaned, "")
    
    def test_format_output_text_only(self):
        """Test output formatting for text only"""
        results = [
            {'text': 'Hello', 'confidence': 0.9},
            {'text': 'World', 'confidence': 0.8}
        ]
        output = format_output(results, text_only=True)
        self.assertEqual(output, "Hello World")
    
    def test_format_output_with_confidence(self):
        """Test output formatting with confidence"""
        results = [
            {'text': 'Hello', 'confidence': 0.9},
            {'text': 'World', 'confidence': 0.8}
        ]
        output = format_output(results, with_confidence=True)
        
        self.assertIn('text', output)
        self.assertIn('confidence', output)
        self.assertEqual(output['text'], "Hello World")
        self.assertEqual(output['confidence'], 0.85)
    
    def test_format_output_detailed(self):
        """Test detailed output formatting"""
        results = [
            {'text': 'Hello', 'confidence': 0.9, 'bbox': {'x': 10, 'y': 10}, 'engine': 'tesseract'},
            {'text': 'World', 'confidence': 0.8, 'bbox': {'x': 70, 'y': 10}, 'engine': 'tesseract'}
        ]
        output = format_output(results, detailed=True)
        
        self.assertIn('text', output)
        self.assertIn('results', output)
        self.assertIn('confidence', output)
        self.assertIn('total_words', output)
        self.assertEqual(output['total_words'], 2)
        self.assertEqual(len(output['results']), 2)
    
    def test_format_output_empty(self):
        """Test output formatting with empty results"""
        output = format_output([], text_only=True)
        self.assertEqual(output, "")
        
        output = format_output([], detailed=True)
        self.assertEqual(output['text'], "")
        self.assertEqual(output['confidence'], 0.0)
        self.assertEqual(output['total_words'], 0)
    
    def test_merge_overlapping_boxes_empty(self):
        """Test merging overlapping boxes with empty list"""
        merged = merge_overlapping_boxes([])
        self.assertEqual(merged, [])
    
    def test_merge_overlapping_boxes_no_overlap(self):
        """Test merging boxes with no overlap"""
        boxes = [
            {'x': 10, 'y': 10, 'width': 50, 'height': 20, 'text': 'Hello'},
            {'x': 100, 'y': 10, 'width': 50, 'height': 20, 'text': 'World'}
        ]
        merged = merge_overlapping_boxes(boxes)
        self.assertEqual(len(merged), 2)
    
    def test_merge_overlapping_boxes_with_overlap(self):
        """Test merging overlapping boxes"""
        boxes = [
            {'x': 10, 'y': 10, 'width': 50, 'height': 20, 'text': 'Hello'},
            {'x': 30, 'y': 15, 'width': 40, 'height': 15, 'text': 'World'}
        ]
        merged = merge_overlapping_boxes(boxes, overlap_threshold=0.1)
        self.assertEqual(len(merged), 1)
        self.assertIn('Hello', merged[0]['text'])
        self.assertIn('World', merged[0]['text'])
    
    def test_validate_ocr_results_empty(self):
        """Test validating empty OCR results"""
        validated = validate_ocr_results([])
        self.assertEqual(validated, [])
    
    def test_validate_ocr_results_valid(self):
        """Test validating valid OCR results"""
        results = [
            {'text': 'Hello', 'confidence': 0.9, 'bbox': {'x': 10}, 'engine': 'tesseract'},
            {'text': 'World', 'confidence': 0.8, 'bbox': {'x': 20}, 'engine': 'easyocr'}
        ]
        validated = validate_ocr_results(results)
        self.assertEqual(len(validated), 2)
        self.assertEqual(validated[0]['text'], 'Hello')
        self.assertEqual(validated[1]['text'], 'World')
    
    def test_validate_ocr_results_invalid(self):
        """Test validating invalid OCR results"""
        results = [
            {'text': '', 'confidence': 0.9},  # Empty text
            {'confidence': 0.8},  # Missing text
            'not a dict',  # Invalid type
            {'text': 'Valid', 'confidence': 1.5},  # Invalid confidence
            {'text': '  Valid  ', 'confidence': 0.7}  # Valid with whitespace
        ]
        validated = validate_ocr_results(results)
        
        # Should only include the valid result with whitespace trimmed
        self.assertEqual(len(validated), 1)
        self.assertEqual(validated[0]['text'], 'Valid')
        self.assertEqual(validated[0]['confidence'], 1.0)  # Clamped to 1.0
    
    def test_validate_ocr_results_missing_fields(self):
        """Test validating results with missing fields"""
        results = [
            {'text': 'Hello'},  # Missing confidence, bbox, engine
            {'text': 'World', 'confidence': 0.8}  # Missing bbox, engine
        ]
        validated = validate_ocr_results(results)
        
        self.assertEqual(len(validated), 2)
        self.assertEqual(validated[0]['confidence'], 0.0)  # Default confidence
        self.assertEqual(validated[0]['engine'], 'unknown')  # Default engine
        self.assertEqual(validated[0]['bbox'], {})  # Default bbox


if __name__ == '__main__':
    unittest.main()
