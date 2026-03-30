"""
Image preprocessing utilities for OCR
"""

import logging
from typing import Union, Tuple, Optional
from pathlib import Path
import tempfile
import os

try:
    import cv2
    import numpy as np
    from PIL import Image, ImageEnhance, ImageFilter
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """
    Advanced image preprocessing for OCR optimization
    """
    
    def __init__(self):
        """Initialize the preprocessor"""
        if not OPENCV_AVAILABLE:
            logger.warning(
                "OpenCV not available. Some preprocessing features will be limited. "
                "Install with: pip install opencv-python pillow"
            )
    
    def process(self, 
                image_path: Union[str, Path],
                operations: Optional[list] = None) -> Union[str, Path]:
        """
        Apply preprocessing operations to an image
        
        Args:
            image_path: Path to the input image
            operations: List of preprocessing operations to apply
            
        Returns:
            Path to the processed image (temp file if processing was applied)
        """
        if operations is None:
            operations = [
                'grayscale',
                'noise_reduction', 
                'contrast_enhancement',
                'thresholding'
            ]
        
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # If no operations specified, return original path
        if not operations:
            return image_path
        
        try:
            # Load image
            if OPENCV_AVAILABLE:
                image = cv2.imread(str(image_path))
                if image is None:
                    # Fallback to PIL if OpenCV fails
                    image = self._load_with_pil(image_path)
                    processed = self._process_with_pil(image, operations)
                else:
                    processed = self._process_with_opencv(image, operations)
            else:
                image = self._load_with_pil(image_path)
                processed = self._process_with_pil(image, operations)
            
            # Save processed image to temp file
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            if isinstance(processed, np.ndarray):
                cv2.imwrite(temp_file.name, processed)
            else:
                processed.save(temp_file.name)
            
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Preprocessing failed: {str(e)}")
            # Return original image if preprocessing fails
            return image_path
    
    def _load_with_pil(self, image_path: Path):
        """Load image using PIL"""
        return Image.open(image_path)
    
    def _process_with_opencv(self, image: np.ndarray, operations: list) -> np.ndarray:
        """Process image using OpenCV"""
        processed = image.copy()
        
        for operation in operations:
            if operation == 'grayscale':
                processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
            elif operation == 'noise_reduction':
                processed = cv2.medianBlur(processed, 3)
            elif operation == 'gaussian_blur':
                processed = cv2.GaussianBlur(processed, (5, 5), 0)
            elif operation == 'contrast_enhancement':
                processed = cv2.convertScaleAbs(processed, alpha=1.2, beta=10)
            elif operation == 'thresholding':
                if len(processed.shape) == 3:
                    processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
                _, processed = cv2.threshold(processed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            elif operation == 'adaptive_thresholding':
                if len(processed.shape) == 3:
                    processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
                processed = cv2.adaptiveThreshold(processed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            elif operation == 'morphology':
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                processed = cv2.morphologyEx(processed, cv2.MORPH_CLOSE, kernel)
            elif operation == 'edge_enhancement':
                kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                processed = cv2.filter2D(processed, -1, kernel)
        
        return processed
    
    def _process_with_pil(self, image: Image.Image, operations: list) -> Image.Image:
        """Process image using PIL (fallback)"""
        processed = image.copy()
        
        for operation in operations:
            if operation == 'grayscale':
                processed = processed.convert('L')
            elif operation == 'contrast_enhancement':
                enhancer = ImageEnhance.Contrast(processed)
                processed = enhancer.enhance(1.5)
            elif operation == 'brightness_enhancement':
                enhancer = ImageEnhance.Brightness(processed)
                processed = enhancer.enhance(1.2)
            elif operation == 'sharpness_enhancement':
                enhancer = ImageEnhance.Sharpness(processed)
                processed = enhancer.enhance(2.0)
            elif operation == 'noise_reduction':
                processed = processed.filter(ImageFilter.MedianFilter(size=3))
            elif operation == 'edge_enhancement':
                processed = processed.filter(ImageFilter.EDGE_ENHANCE)
        
        return processed
    
    def deskew(self, image_path: Union[str, Path]) -> Union[str, Path]:
        """
        Deskew an image to correct text alignment
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Path to the deskewed image
        """
        if not OPENCV_AVAILABLE:
            logger.warning("OpenCV not available, skipping deskew")
            return image_path
        
        image_path = Path(image_path)
        
        try:
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                return image_path
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect edges
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Detect lines using Hough transform
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                # Calculate angle
                angles = []
                for rho, theta in lines[:, 0]:
                    angle = theta * 180 / np.pi
                    if angle < 45:
                        angles.append(angle)
                    elif angle > 135:
                        angles.append(angle - 180)
                
                if angles:
                    median_angle = np.median(angles)
                    
                    # Rotate image to correct skew
                    if abs(median_angle) > 0.5:
                        (h, w) = image.shape[:2]
                        center = (w // 2, h // 2)
                        M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                        rotated = cv2.warpAffine(image, M, (w, h), 
                                              flags=cv2.INTER_CUBIC, 
                                              borderMode=cv2.BORDER_REPLICATE)
                        
                        # Save rotated image
                        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                        cv2.imwrite(temp_file.name, rotated)
                        return temp_file.name
            
            return image_path
            
        except Exception as e:
            logger.error(f"Deskew failed: {str(e)}")
            return image_path
    
    def enhance_for_ocr(self, image_path: Union[str, Path]) -> Union[str, Path]:
        """
        Apply comprehensive enhancement optimized for OCR
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Path to the enhanced image
        """
        operations = [
            'grayscale',
            'noise_reduction',
            'contrast_enhancement',
            'adaptive_thresholding'
        ]
        
        return self.process(image_path, operations)
