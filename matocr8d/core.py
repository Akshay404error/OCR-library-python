"""
Core OCR functionality for matocr8d library
"""

import os
from typing import Optional, Union, List, Dict, Any
from PIL import Image
import pytesseract

from .exceptions import OCRError, ImageLoadError, UnsupportedFormatError


class MatOCR8D:
    """
    Main OCR class for extracting text from images
    """
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
    
    def __init__(self, language: str = 'eng', tesseract_cmd: Optional[str] = None):
        """
        Initialize the OCR engine
        
        Args:
            language: Language code for OCR (default: 'eng' for English)
            tesseract_cmd: Path to tesseract executable (optional)
        """
        self.language = language
        
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    def _validate_image_path(self, image_path: str) -> None:
        """Validate that the image path exists and has supported format"""
        if not os.path.exists(image_path):
            raise ImageLoadError(f"Image file not found: {image_path}")
        
        ext = os.path.splitext(image_path)[1].lower()
        if ext not in self.SUPPORTED_FORMATS:
            raise UnsupportedFormatError(
                f"Unsupported image format: {ext}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )
    
    def _load_image(self, image_input: Union[str, Image.Image]) -> Image.Image:
        """Load image from path or PIL Image object"""
        if isinstance(image_input, str):
            self._validate_image_path(image_input)
            try:
                image = Image.open(image_input)
            except Exception as e:
                raise ImageLoadError(f"Failed to load image: {e}")
        elif isinstance(image_input, Image.Image):
            image = image_input
        else:
            raise ImageLoadError("Input must be a file path or PIL Image object")
        
        return image
    
    def extract_text(self, image_input: Union[str, Image.Image]) -> str:
        """
        Extract text from an image
        
        Args:
            image_input: Path to image file or PIL Image object
            
        Returns:
            Extracted text as string
            
        Raises:
            OCRError: If OCR processing fails
        """
        try:
            image = self._load_image(image_input)
            text = pytesseract.image_to_string(image, lang=self.language)
            return text.strip()
        except Exception as e:
            if isinstance(e, (ImageLoadError, UnsupportedFormatError)):
                raise
            raise OCRError(f"OCR processing failed: {e}")
    
    def extract_text_with_data(self, image_input: Union[str, Image.Image]) -> Dict[str, Any]:
        """
        Extract text with additional metadata from an image
        
        Args:
            image_input: Path to image file or PIL Image object
            
        Returns:
            Dictionary containing text and metadata
        """
        try:
            image = self._load_image(image_input)
            
            # Get OCR data with bounding boxes
            data = pytesseract.image_to_data(image, lang=self.language, output_type=pytesseract.Output.DICT)
            
            # Extract full text
            full_text = pytesseract.image_to_string(image, lang=self.language)
            
            return {
                'text': full_text.strip(),
                'raw_data': data,
                'confidence': self._calculate_average_confidence(data),
                'word_count': len([word for word in data['text'] if word.strip()])
            }
        except Exception as e:
            if isinstance(e, (ImageLoadError, UnsupportedFormatError)):
                raise
            raise OCRError(f"OCR processing failed: {e}")
    
    def _calculate_average_confidence(self, data: Dict[str, List]) -> float:
        """Calculate average confidence from OCR data"""
        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
        return sum(confidences) / len(confidences) if confidences else 0.0
    
    def extract_text_blocks(self, image_input: Union[str, Image.Image]) -> List[Dict[str, Any]]:
        """
        Extract text blocks with their bounding boxes
        
        Args:
            image_input: Path to image file or PIL Image object
            
        Returns:
            List of dictionaries containing text blocks with coordinates
        """
        try:
            image = self._load_image(image_input)
            data = pytesseract.image_to_data(image, lang=self.language, output_type=pytesseract.Output.DICT)
            
            blocks = []
            for i in range(len(data['text'])):
                if data['text'][i].strip():
                    blocks.append({
                        'text': data['text'][i],
                        'confidence': int(data['conf'][i]),
                        'bbox': {
                            'x': data['left'][i],
                            'y': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i]
                        }
                    })
            
            return blocks
        except Exception as e:
            if isinstance(e, (ImageLoadError, UnsupportedFormatError)):
                raise
            raise OCRError(f"OCR processing failed: {e}")
    
    def get_available_languages(self) -> List[str]:
        """
        Get list of available languages for OCR
        
        Returns:
            List of available language codes
        """
        try:
            return pytesseract.get_languages(config='')
        except Exception as e:
            raise OCRError(f"Failed to get available languages: {e}")
