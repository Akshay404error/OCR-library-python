"""
Core OCR functionality for matocr8d library
"""

import os
import logging
from typing import Dict, List, Optional, Union, Any
from pathlib import Path

from .engines import OCREngine, TesseractEngine, EasyOCREngine, PaddleOCREngine
from .preprocessing import ImagePreprocessor
from .utils import confidence_score, text_cleanup, format_output

logger = logging.getLogger(__name__)


class MatOCR8D:
    """
    Advanced OCR engine with support for multiple backends and preprocessing
    """
    
    def __init__(self, 
                 engine: str = "tesseract",
                 language: Union[str, List[str]] = "eng",
                 preprocessing: bool = True,
                 confidence_threshold: float = 0.5,
                 **kwargs):
        """
        Initialize the OCR engine
        
        Args:
            engine: OCR engine to use ('tesseract', 'easyocr', 'paddleocr')
            language: Language(s) for OCR
            preprocessing: Whether to apply image preprocessing
            confidence_threshold: Minimum confidence score for text extraction
            **kwargs: Additional engine-specific parameters
        """
        self.engine_name = engine.lower()
        self.language = language
        self.preprocessing = preprocessing
        self.confidence_threshold = confidence_threshold
        self.engine_kwargs = kwargs
        
        # Initialize OCR engine
        self.engine = self._initialize_engine()
        
        # Initialize preprocessor if needed
        if preprocessing:
            self.preprocessor = ImagePreprocessor()
        else:
            self.preprocessor = None
            
        logger.info(f"Initialized MatOCR8D with engine: {engine}")
    
    def _initialize_engine(self) -> OCREngine:
        """Initialize the specified OCR engine"""
        engines = {
            "tesseract": TesseractEngine,
            "easyocr": EasyOCREngine,
            "paddleocr": PaddleOCREngine
        }
        
        if self.engine_name not in engines:
            raise ValueError(f"Unsupported engine: {self.engine_name}. "
                           f"Supported engines: {list(engines.keys())}")
        
        return engines[self.engine_name](language=self.language, **self.engine_kwargs)
    
    def extract_text(self, 
                    image_path: Union[str, Path],
                    preprocess: Optional[bool] = None,
                    return_confidence: bool = False,
                    return_details: bool = False) -> Union[str, Dict[str, Any]]:
        """
        Extract text from an image
        
        Args:
            image_path: Path to the image file
            preprocess: Whether to apply preprocessing (overrides instance setting)
            return_confidence: Whether to return confidence scores
            return_details: Whether to return detailed results
            
        Returns:
            Extracted text or detailed results dictionary
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Apply preprocessing if needed
        if preprocess is None:
            preprocess = self.preprocessing
            
        processed_image = image_path
        if preprocess and self.preprocessor:
            processed_image = self.preprocessor.process(image_path)
        
        # Extract text using the selected engine
        try:
            results = self.engine.extract_text(processed_image)
            
            # Filter by confidence threshold
            if self.confidence_threshold > 0:
                results = self._filter_by_confidence(results)
            
            # Format output
            if return_details:
                return format_output(results, detailed=True)
            elif return_confidence:
                return format_output(results, with_confidence=True)
            else:
                return format_output(results, text_only=True)
                
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            raise
    
    def extract_text_batch(self, 
                          image_paths: List[Union[str, Path]],
                          **kwargs) -> List[Union[str, Dict[str, Any]]]:
        """
        Extract text from multiple images
        
        Args:
            image_paths: List of image file paths
            **kwargs: Additional arguments for extract_text
            
        Returns:
            List of extracted text or detailed results
        """
        results = []
        for image_path in image_paths:
            try:
                result = self.extract_text(image_path, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {image_path}: {str(e)}")
                results.append({"error": str(e), "file": str(image_path)})
        
        return results
    
    def _filter_by_confidence(self, results: List[Dict]) -> List[Dict]:
        """Filter OCR results by confidence threshold"""
        if not results:
            return results
            
        filtered = []
        for result in results:
            if isinstance(result, dict) and 'confidence' in result:
                if result['confidence'] >= self.confidence_threshold:
                    filtered.append(result)
            else:
                # If no confidence info, include by default
                filtered.append(result)
        
        return filtered
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages for the current engine"""
        return self.engine.get_supported_languages()
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about the current OCR engine"""
        return {
            "engine": self.engine_name,
            "version": self.engine.get_version(),
            "supported_languages": self.get_supported_languages(),
            "preprocessing_enabled": self.preprocessing,
            "confidence_threshold": self.confidence_threshold
        }
