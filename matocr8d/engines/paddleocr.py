"""
PaddleOCR Engine implementation
"""

import logging
from typing import List, Dict, Any, Union
from pathlib import Path

try:
    from paddleocr import PaddleOCR as PaddleOCRBase
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False

from .base import OCREngine

logger = logging.getLogger(__name__)


class PaddleOCREngine(OCREngine):
    """
    PaddleOCR engine implementation
    """
    
    def __init__(self, language: Union[str, List[str]] = "en", **kwargs):
        """
        Initialize PaddleOCR engine
        
        Args:
            language: Language(s) for OCR
            **kwargs: Additional PaddleOCR parameters
        """
        super().__init__(language, **kwargs)
        
        if not PADDLEOCR_AVAILABLE:
            raise ImportError(
                "PaddleOCR not found. Install with: pip install paddleocr"
            )
        
        # Map language codes to PaddleOCR language codes
        self.lang_code = self._map_language_code()
        
        # Initialize PaddleOCR
        use_angle_cls = self.kwargs.get('use_angle_cls', True)
        use_gpu = self.kwargs.get('use_gpu', False)
        show_log = self.kwargs.get('show_log', False)
        
        try:
            self.ocr = PaddleOCRBase(
                use_angle_cls=use_angle_cls,
                lang=self.lang_code,
                use_gpu=use_gpu,
                show_log=show_log
            )
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {str(e)}")
            raise
    
    def _map_language_code(self) -> str:
        """Map language codes to PaddleOCR language codes"""
        lang_mapping = {
            'en': 'en',
            'eng': 'en',
            'ch': 'ch',
            'chinese': 'ch',
            'zh': 'ch',
            'japan': 'japan',
            'ja': 'japan',
            'korean': 'korean',
            'ko': 'korean',
            'fr': 'french',
            'french': 'french',
            'german': 'german',
            'de': 'german',
            'spanish': 'spanish',
            'es': 'spanish'
        }
        
        if isinstance(self.language, list):
            # Use first language for PaddleOCR
            lang = self.language[0].lower()
        else:
            lang = self.language.lower()
        
        return lang_mapping.get(lang, 'en')
    
    def extract_text(self, image_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Extract text using PaddleOCR
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of dictionaries with extracted text and metadata
        """
        if not self.validate_image(image_path):
            raise ValueError(f"Invalid image file: {image_path}")
        
        try:
            # Extract text using PaddleOCR
            results = self.ocr.ocr(str(image_path), cls=True)
            
            formatted_results = []
            
            if results and results[0]:  # Check if results exist and are not empty
                for line in results[0]:
                    if line and len(line) >= 2:
                        bbox_points = line[0]
                        text_info = line[1]
                        
                        if text_info and len(text_info) >= 2:
                            text = text_info[0]
                            confidence = text_info[1]
                            
                            # Calculate bounding box from points
                            x_coords = [point[0] for point in bbox_points]
                            y_coords = [point[1] for point in bbox_points]
                            
                            result = {
                                'text': text,
                                'confidence': confidence,
                                'bbox': {
                                    'x': min(x_coords),
                                    'y': min(y_coords),
                                    'width': max(x_coords) - min(x_coords),
                                    'height': max(y_coords) - min(y_coords)
                                },
                                'engine': 'paddleocr'
                            }
                            formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"PaddleOCR extraction failed: {str(e)}")
            raise
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported PaddleOCR languages"""
        return [
            'en', 'ch', 'japan', 'korean', 'french', 'german', 'spanish',
            'tamil', 'telugu', 'kannada', 'arabic', 'tibetan', 'japanese',
            'chinese_cht', 'chinese', 'hebrew', 'russian', 'latin'
        ]
    
    def get_version(self) -> str:
        """Get PaddleOCR version"""
        try:
            import paddleocr
            return paddleocr.__version__
        except Exception:
            return "Unknown"
