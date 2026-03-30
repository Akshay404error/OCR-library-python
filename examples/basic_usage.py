"""
Basic usage examples for matocr8d
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import matocr8d
sys.path.insert(0, str(Path(__file__).parent.parent))

from matocr8d import MatOCR8D

def basic_tesseract_example():
    """Basic example using Tesseract engine"""
    print("=== Basic Tesseract Example ===")
    
    # Initialize OCR with Tesseract
    ocr = MatOCR8D(engine="tesseract", language="eng")
    
    # Note: You'll need to provide an actual image file
    # For this example, we'll show the API usage
    print("OCR initialized with Tesseract engine")
    
    # Example usage (uncomment when you have an image file):
    # try:
    #     text = ocr.extract_text("sample_image.jpg")
    #     print(f"Extracted text: {text}")
    # except FileNotFoundError:
    #     print("Please provide a valid image file")
    
    print("Engine info:", ocr.get_engine_info())
    print()

def easyocr_example():
    """Example using EasyOCR engine"""
    print("=== EasyOCR Example ===")
    
    try:
        # Initialize OCR with EasyOCR
        ocr = MatOCR8D(engine="easyocr", language="en")
        print("OCR initialized with EasyOCR engine")
        
        # Example usage (uncomment when you have an image file):
        # result = ocr.extract_text("sample_image.jpg", return_confidence=True)
        # print(f"Text: {result['text']}")
        # print(f"Confidence: {result['confidence']}")
        
        print("Engine info:", ocr.get_engine_info())
        
    except ImportError:
        print("EasyOCR not installed. Install with: pip install easyocr")
    
    print()

def paddleocr_example():
    """Example using PaddleOCR engine"""
    print("=== PaddleOCR Example ===")
    
    try:
        # Initialize OCR with PaddleOCR
        ocr = MatOCR8D(engine="paddleocr", language="en")
        print("OCR initialized with PaddleOCR engine")
        
        # Example usage (uncomment when you have an image file):
        # result = ocr.extract_text("sample_image.jpg", return_details=True)
        # print(f"Extracted: {result['text']}")
        # print(f"Total words: {result['total_words']}")
        
        print("Engine info:", ocr.get_engine_info())
        
    except ImportError:
        print("PaddleOCR not installed. Install with: pip install paddleocr")
    
    print()

def advanced_example():
    """Advanced example with preprocessing and confidence filtering"""
    print("=== Advanced Example ===")
    
    # Initialize with advanced settings
    ocr = MatOCR8D(
        engine="tesseract",
        language="eng",
        preprocessing=True,
        confidence_threshold=0.7
    )
    
    print("OCR initialized with preprocessing and confidence threshold")
    
    # Example of batch processing (uncomment when you have image files):
    # image_paths = ["image1.jpg", "image2.jpg", "image3.jpg"]
    # results = ocr.extract_text_batch(image_paths)
    # 
    # for i, result in enumerate(results):
    #     print(f"Image {i+1}: {result}")
    
    print("Supported languages:", ocr.get_supported_languages())
    print()

def multilingual_example():
    """Example with multiple languages"""
    print("=== Multilingual Example ===")
    
    try:
        # Initialize for multiple languages
        ocr = MatOCR8D(engine="easyocr", language=["en", "fr", "de"])
        print("OCR initialized for English, French, and German")
        
        # Example usage (uncomment when you have an image file):
        # result = ocr.extract_text("multilingual_doc.jpg", return_details=True)
        # 
        # for word_info in result['results']:
        #     print(f"Text: {word_info['text']}")
        #     print(f"Confidence: {word_info['confidence']}")
        
        print("Engine info:", ocr.get_engine_info())
        
    except ImportError:
        print("EasyOCR not installed for multilingual support")
    
    print()

if __name__ == "__main__":
    print("MatOCR8D - Basic Usage Examples")
    print("=" * 40)
    print()
    
    basic_tesseract_example()
    easyocr_example()
    paddleocr_example()
    advanced_example()
    multilingual_example()
    
    print("To run these examples with actual images:")
    print("1. Install the required OCR engines:")
    print("   pip install matocr8d[tesseract]  # or [easyocr], [paddleocr], [all]")
    print("2. Place your test images in the examples directory")
    print("3. Uncomment the relevant code sections")
    print("4. Run the script")
