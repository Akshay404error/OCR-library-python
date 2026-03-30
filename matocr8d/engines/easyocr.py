"""
EasyOCR Engine implementation
"""

import logging
from typing import List, Dict, Any, Union
from pathlib import Path

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

from .base import OCREngine

logger = logging.getLogger(__name__)


class EasyOCREngine(OCREngine):
    """
    EasyOCR engine implementation
    """
    
    def __init__(self, language: Union[str, List[str]] = "en", **kwargs):
        """
        Initialize EasyOCR engine
        
        Args:
            language: Language(s) for OCR (EasyOCR uses language codes like 'en', 'ch_sim')
            **kwargs: Additional EasyOCR parameters
        """
        super().__init__(language, **kwargs)
        
        if not EASYOCR_AVAILABLE:
            raise ImportError(
                "EasyOCR not found. Install with: pip install easyocr"
            )
        
        # Convert language to list format
        if isinstance(self.language, str):
            self.language_list = [self.language]
        else:
            self.language_list = self.language
        
        # Initialize EasyOCR reader
        gpu = self.kwargs.get('gpu', True)
        model_storage_directory = self.kwargs.get('model_storage_directory')
        download_enabled = self.kwargs.get('download_enabled', True)
        
        try:
            self.reader = easyocr.Reader(
                self.language_list,
                gpu=gpu,
                model_storage_directory=model_storage_directory,
                download_enabled=download_enabled
            )
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR reader: {str(e)}")
            raise
    
    def extract_text(self, image_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Extract text using EasyOCR
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of dictionaries with extracted text and metadata
        """
        if not self.validate_image(image_path):
            raise ValueError(f"Invalid image file: {image_path}")
        
        try:
            # Extract text using EasyOCR
            results = self.reader.readtext(str(image_path))
            
            # Format results
            formatted_results = []
            for (bbox, text, confidence) in results:
                # EasyOCR bbox format: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                
                result = {
                    'text': text,
                    'confidence': confidence,
                    'bbox': {
                        'x': min(x_coords),
                        'y': min(y_coords),
                        'width': max(x_coords) - min(x_coords),
                        'height': max(y_coords) - min(y_coords)
                    },
                    'engine': 'easyocr'
                }
                formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"EasyOCR extraction failed: {str(e)}")
            raise
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported EasyOCR languages"""
        # EasyOCR supports many languages, return common ones
        return [
            'en', 'ch_sim', 'ch_tra', 'ja', 'ko', 'ar', 'ru', 'de', 'fr', 
            'es', 'it', 'pt', 'nl', 'sv', 'no', 'da', 'fi', 'pl', 'tr', 'he',
            'hi', 'bn', 'ta', 'te', 'kn', 'ml', 'th', 'vi', 'id', 'ms'
        ]
    
    def get_version(self) -> str:
        """Get EasyOCR version"""
        try:
            import easyocr
            return easyocr.__version__
        except Exception:
            return "Unknown"
