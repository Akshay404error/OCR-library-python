"""
Tests for core OCR functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from matocr8d.core import MatOCR8D
from matocr8d.engines.base import OCREngine


class TestMatOCR8D(unittest.TestCase):
    """Test cases for MatOCR8D core class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = Path(self.temp_dir) / "test_image.jpg"
        
        # Create a dummy image file
        with open(self.test_image_path, 'wb') as f:
            f.write(b'fake image data')
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization_tesseract(self):
        """Test initialization with Tesseract engine"""
        with patch('matocr8d.engines.tesseract.TesseractEngine') as mock_engine:
            mock_engine_instance = Mock()
            mock_engine.return_value = mock_engine_instance
            
            ocr = MatOCR8D(engine="tesseract", language="eng")
            
            self.assertEqual(ocr.engine_name, "tesseract")
            self.assertEqual(ocr.language, "eng")
            self.assertTrue(ocr.preprocessing)
            self.assertEqual(ocr.confidence_threshold, 0.5)
            mock_engine.assert_called_once_with(language="eng")
    
    def test_initialization_unsupported_engine(self):
        """Test initialization with unsupported engine"""
        with self.assertRaises(ValueError) as context:
            MatOCR8D(engine="unsupported_engine")
        
        self.assertIn("Unsupported engine", str(context.exception))
    
    def test_extract_text_file_not_found(self):
        """Test extract_text with non-existent file"""
        with patch('matocr8d.engines.tesseract.TesseractEngine'):
            ocr = MatOCR8D(engine="tesseract")
            
            with self.assertRaises(FileNotFoundError):
                ocr.extract_text("non_existent_file.jpg")
    
    def test_extract_text_success(self):
        """Test successful text extraction"""
        mock_results = [
            {'text': 'Hello', 'confidence': 0.95, 'bbox': {'x': 10, 'y': 10, 'width': 50, 'height': 20}},
            {'text': 'World', 'confidence': 0.87, 'bbox': {'x': 70, 'y': 10, 'width': 50, 'height': 20}}
        ]
        
        with patch('matocr8d.engines.tesseract.TesseractEngine') as mock_engine_class:
            mock_engine_instance = Mock()
            mock_engine_instance.extract_text.return_value = mock_results
            mock_engine_class.return_value = mock_engine_instance
            
            ocr = MatOCR8D(engine="tesseract")
            
            result = ocr.extract_text(self.test_image_path)
            
            self.assertEqual(result, "Hello World")
            mock_engine_instance.extract_text.assert_called_once()
    
    def test_extract_text_with_confidence(self):
        """Test text extraction with confidence scores"""
        mock_results = [
            {'text': 'Test', 'confidence': 0.92, 'bbox': {'x': 10, 'y': 10, 'width': 40, 'height': 20}}
        ]
        
        with patch('matocr8d.engines.tesseract.TesseractEngine') as mock_engine_class:
            mock_engine_instance = Mock()
            mock_engine_instance.extract_text.return_value = mock_results
            mock_engine_class.return_value = mock_engine_instance
            
            ocr = MatOCR8D(engine="tesseract")
            
            result = ocr.extract_text(self.test_image_path, return_confidence=True)
            
            self.assertIn('text', result)
            self.assertIn('confidence', result)
            self.assertEqual(result['text'], "Test")
            self.assertEqual(result['confidence'], 0.92)
    
    def test_extract_text_with_details(self):
        """Test text extraction with detailed results"""
        mock_results = [
            {'text': 'Detailed', 'confidence': 0.88, 'bbox': {'x': 10, 'y': 10, 'width': 60, 'height': 20}}
        ]
        
        with patch('matocr8d.engines.tesseract.TesseractEngine') as mock_engine_class:
            mock_engine_instance = Mock()
            mock_engine_instance.extract_text.return_value = mock_results
            mock_engine_class.return_value = mock_engine_instance
            
            ocr = MatOCR8D(engine="tesseract")
            
            result = ocr.extract_text(self.test_image_path, return_details=True)
            
            self.assertIn('text', result)
            self.assertIn('results', result)
            self.assertIn('confidence', result)
            self.assertIn('total_words', result)
            self.assertEqual(result['total_words'], 1)
    
    def test_extract_text_batch(self):
        """Test batch text extraction"""
        mock_results = [{'text': 'Batch', 'confidence': 0.90}]
        
        with patch('matocr8d.engines.tesseract.TesseractEngine') as mock_engine_class:
            mock_engine_instance = Mock()
            mock_engine_instance.extract_text.return_value = mock_results
            mock_engine_class.return_value = mock_engine_instance
            
            ocr = MatOCR8D(engine="tesseract")
            
            # Create another test image
            test_image2 = Path(self.temp_dir) / "test_image2.jpg"
            with open(test_image2, 'wb') as f:
                f.write(b'fake image data 2')
            
            results = ocr.extract_text_batch([self.test_image_path, test_image2])
            
            self.assertEqual(len(results), 2)
            self.assertEqual(mock_engine_instance.extract_text.call_count, 2)
    
    def test_confidence_threshold_filtering(self):
        """Test confidence threshold filtering"""
        mock_results = [
            {'text': 'High', 'confidence': 0.95},
            {'text': 'Low', 'confidence': 0.30},
            {'text': 'Medium', 'confidence': 0.75}
        ]
        
        with patch('matocr8d.engines.tesseract.TesseractEngine') as mock_engine_class:
            mock_engine_instance = Mock()
            mock_engine_instance.extract_text.return_value = mock_results
            mock_engine_class.return_value = mock_engine_instance
            
            ocr = MatOCR8D(engine="tesseract", confidence_threshold=0.7)
            
            result = ocr.extract_text(self.test_image_path)
            
            # Should only include high and medium confidence results
            self.assertEqual(result, "High Medium")
    
    def test_get_supported_languages(self):
        """Test getting supported languages"""
        with patch('matocr8d.engines.tesseract.TesseractEngine') as mock_engine_class:
            mock_engine_instance = Mock()
            mock_engine_instance.get_supported_languages.return_value = ['eng', 'fra', 'deu']
            mock_engine_class.return_value = mock_engine_instance
            
            ocr = MatOCR8D(engine="tesseract")
            languages = ocr.get_supported_languages()
            
            self.assertEqual(languages, ['eng', 'fra', 'deu'])
    
    def test_get_engine_info(self):
        """Test getting engine information"""
        with patch('matocr8d.engines.tesseract.TesseractEngine') as mock_engine_class:
            mock_engine_instance = Mock()
            mock_engine_instance.get_version.return_value = "5.3.0"
            mock_engine_instance.get_supported_languages.return_value = ['eng', 'fra']
            mock_engine_class.return_value = mock_engine_instance
            
            ocr = MatOCR8D(engine="tesseract", confidence_threshold=0.8)
            info = ocr.get_engine_info()
            
            self.assertEqual(info['engine'], 'tesseract')
            self.assertEqual(info['version'], '5.3.0')
            self.assertEqual(info['supported_languages'], ['eng', 'fra'])
            self.assertTrue(info['preprocessing_enabled'])
            self.assertEqual(info['confidence_threshold'], 0.8)


class TestOCREngineBase(unittest.TestCase):
    """Test cases for OCREngine base class"""
    
    def test_validate_image_valid_file(self):
        """Test image validation with valid file"""
        temp_dir = tempfile.mkdtemp()
        test_image = Path(temp_dir) / "test.jpg"
        
        with open(test_image, 'wb') as f:
            f.write(b'fake image data')
        
        try:
            # Create a concrete implementation for testing
            class TestEngine(OCREngine):
                def extract_text(self, image_path):
                    return []
                def get_supported_languages(self):
                    return []
                def get_version(self):
                    return "test"
            
            engine = TestEngine()
            self.assertTrue(engine.validate_image(test_image))
            
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_validate_image_invalid_extension(self):
        """Test image validation with invalid extension"""
        temp_dir = tempfile.mkdtemp()
        test_file = Path(temp_dir) / "test.txt"
        
        with open(test_file, 'w') as f:
            f.write("not an image")
        
        try:
            class TestEngine(OCREngine):
                def extract_text(self, image_path):
                    return []
                def get_supported_languages(self):
                    return []
                def get_version(self):
                    return "test"
            
            engine = TestEngine()
            self.assertFalse(engine.validate_image(test_file))
            
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_validate_image_non_existent(self):
        """Test image validation with non-existent file"""
        class TestEngine(OCREngine):
            def extract_text(self, image_path):
                return []
            def get_supported_languages(self):
                return []
            def get_version(self):
                return "test"
        
        engine = TestEngine()
        self.assertFalse(engine.validate_image("non_existent.jpg"))


if __name__ == '__main__':
    unittest.main()
