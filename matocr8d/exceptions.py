"""
Custom exceptions for matocr8d library
"""


class OCRError(Exception):
    """Base exception for OCR-related errors"""
    pass


class ImageLoadError(OCRError):
    """Raised when an image cannot be loaded or processed"""
    pass


class UnsupportedFormatError(OCRError):
    """Raised when an unsupported image format is provided"""
    pass
