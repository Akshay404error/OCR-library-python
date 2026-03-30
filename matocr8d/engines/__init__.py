"""
OCR Engine implementations for matocr8d
"""

from .base import OCREngine
from .tesseract import TesseractEngine
from .easyocr import EasyOCREngine
from .paddleocr import PaddleOCREngine

__all__ = ["OCREngine", "TesseractEngine", "EasyOCREngine", "PaddleOCREngine"]
