"""
Base class for OCR engines
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union
from pathlib import Path


class OCREngine(ABC):
    """
    Abstract base class for OCR engines
    """
    
    def __init__(self, language: Union[str, List[str]] = "eng", **kwargs):
        """
        Initialize the OCR engine
        
        Args:
            language: Language(s) for OCR
            **kwargs: Engine-specific parameters
        """
        self.language = language
        self.kwargs = kwargs
    
    @abstractmethod
    def extract_text(self, image_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Extract text from an image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of dictionaries containing extracted text and metadata
        """
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Get engine version"""
        pass
    
    def validate_image(self, image_path: Union[str, Path]) -> bool:
        """
        Validate if the image file is supported
        
        Args:
            image_path: Path to the image file
            
        Returns:
            True if image is valid, False otherwise
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            return False
        
        # Check file extension
        supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
        return image_path.suffix.lower() in supported_extensions
