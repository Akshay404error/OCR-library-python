"""
matocr8d - Advanced OCR Library

A powerful Python library for optical character recognition with support for
multiple OCR engines, advanced preprocessing, and comprehensive text extraction capabilities.
"""

__version__ = "1.0.0"
__author__ = "MatOCR8D Team"
__email__ = "contact@matocr8d.com"

from .core import MatOCR8D
from .preprocessing import ImagePreprocessor
from .engines import TesseractEngine, EasyOCREngine, PaddleOCREngine
from .utils import confidence_score, text_cleanup, format_output

__all__ = [
    "MatOCR8D",
    "ImagePreprocessor", 
    "TesseractEngine",
    "EasyOCREngine", 
    "PaddleOCREngine",
    "confidence_score",
    "text_cleanup",
    "format_output"
]
