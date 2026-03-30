"""
Tesseract OCR Engine implementation
"""

import logging
import subprocess
import json
from typing import List, Dict, Any, Union
from pathlib import Path

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

from .base import OCREngine

logger = logging.getLogger(__name__)


class TesseractEngine(OCREngine):
    """
    Tesseract OCR engine implementation
    """
    
    def __init__(self, language: Union[str, List[str]] = "eng", **kwargs):
        """
        Initialize Tesseract engine
        
        Args:
            language: Language(s) for OCR
            **kwargs: Additional Tesseract parameters
        """
        super().__init__(language, **kwargs)
        
        if not TESSERACT_AVAILABLE:
            raise ImportError(
                "Tesseract dependencies not found. Install with: "
                "pip install pytesseract pillow"
            )
        
        # Convert language to string format
        if isinstance(self.language, list):
            self.language_str = "+".join(self.language)
        else:
            self.language_str = self.language
        
        # Set Tesseract path if provided
        if 'tesseract_path' in self.kwargs:
            pytesseract.pytesseract.tesseract_cmd = self.kwargs['tesseract_path']
        
        # Verify Tesseract installation
        try:
            subprocess.run(['tesseract', '--version'], 
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "Tesseract not found. Please install Tesseract OCR engine: "
                "https://github.com/tesseract-ocr/tesseract"
            )
    
    def extract_text(self, image_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Extract text using Tesseract OCR
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of dictionaries with extracted text and metadata
        """
        if not self.validate_image(image_path):
            raise ValueError(f"Invalid image file: {image_path}")
        
        try:
            # Open image
            image = Image.open(image_path)
            
            # Get OCR data with confidence scores
            ocr_data = pytesseract.image_to_data(
                image, 
                lang=self.language_str,
                output_type=pytesseract.Output.DICT,
                **{k: v for k, v in self.kwargs.items() 
                   if k not in ['tesseract_path']}
            )
            
            # Process OCR data
            results = []
            n_boxes = len(ocr_data['text'])
            
            for i in range(n_boxes):
                text = ocr_data['text'][i].strip()
                if text:  # Skip empty text
                    confidence = int(ocr_data['conf'][i]) / 100.0
                    
                    result = {
                        'text': text,
                        'confidence': confidence,
                        'bbox': {
                            'x': ocr_data['left'][i],
                            'y': ocr_data['top'][i],
                            'width': ocr_data['width'][i],
                            'height': ocr_data['height'][i]
                        },
                        'engine': 'tesseract'
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {str(e)}")
            raise
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported Tesseract languages"""
        try:
            # Get available languages from Tesseract
            result = subprocess.run(['tesseract', '--list-langs'], 
                                  capture_output=True, text=True, check=True)
            languages = result.stdout.strip().split('\n')[1:]  # Skip first line
            return [lang.strip() for lang in languages if lang.strip()]
        except Exception as e:
            logger.warning(f"Could not get Tesseract languages: {str(e)}")
            return ['eng']  # Default to English
    
    def get_version(self) -> str:
        """Get Tesseract version"""
        try:
            result = subprocess.run(['tesseract', '--version'], 
                                  capture_output=True, text=True, check=True)
            first_line = result.stdout.split('\n')[0]
            return first_line.split(' ')[1] if len(first_line.split(' ')) > 1 else "Unknown"
        except Exception:
            return "Unknown"
