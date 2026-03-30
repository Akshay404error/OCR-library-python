# MatOCR8D - Advanced OCR Library

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/matocr8d.svg)](https://pypi.org/project/matocr8d/)
[![Build Status](https://img.shields.io/travis/yourusername/matocr8d.svg)](https://travis-ci.com/yourusername/matocr8d)
[![Documentation](https://img.shields.io/readthedocs/matocr8d/latest.svg)](https://matocr8d.readthedocs.io/)

MatOCR8D is a powerful and flexible Python library for optical character recognition (OCR) that supports multiple OCR engines and provides advanced image preprocessing capabilities. It's designed to be easy to use while offering professional-grade features for text extraction from images.

## Features

- **Multiple OCR Engines**: Support for Tesseract, EasyOCR, and PaddleOCR
- **Advanced Preprocessing**: Image enhancement, deskewing, noise reduction
- **Confidence Scoring**: Get confidence scores for extracted text
- **Multi-language Support**: Support for 80+ languages across different engines
- **Batch Processing**: Process multiple images efficiently
- **Flexible Output Formats**: Choose between simple text or detailed results
- **Easy Integration**: Simple API with sensible defaults

## Installation

### Basic Installation

```bash
pip install matocr8d
```

### With Specific OCR Engine

```bash
# For Tesseract support
pip install matocr8d[tesseract]

# For EasyOCR support  
pip install matocr8d[easyocr]

# For PaddleOCR support
pip install matocr8d[paddleocr]

# For all engines
pip install matocr8d[all]
```

### Development Installation

```bash
git clone https://github.com/yourusername/matocr8d.git
cd matocr8d
pip install -e .[dev]
```

## Quick Start

### Basic Usage

```python
from matocr8d import MatOCR8D

# Initialize with default Tesseract engine
ocr = MatOCR8D()

# Extract text from an image
text = ocr.extract_text("image.jpg")
print(text)
```

### Using Different Engines

```python
# Using EasyOCR
ocr = MatOCR8D(engine="easyocr", language="en")

# Using PaddleOCR
ocr = MatOCR8D(engine="paddleocr", language="ch")

# Extract text with confidence scores
result = ocr.extract_text("image.jpg", return_confidence=True)
print(f"Text: {result['text']}")
print(f"Confidence: {result['confidence']}")
```

### Advanced Usage

```python
# With preprocessing and custom confidence threshold
ocr = MatOCR8D(
    engine="tesseract",
    language="eng",
    preprocessing=True,
    confidence_threshold=0.7
)

# Get detailed results
result = ocr.extract_text("document.png", return_details=True)
print(f"Extracted: {result['text']}")
print(f"Total words: {result['total_words']}")
print(f"Average confidence: {result['confidence']}")

# Process multiple images
image_paths = ["page1.jpg", "page2.jpg", "page3.jpg"]
results = ocr.extract_text_batch(image_paths)
for i, result in enumerate(results):
    print(f"Page {i+1}: {result}")
```

## OCR Engines

### Tesseract

- **Installation**: Install Tesseract OCR engine on your system
  - Ubuntu: `sudo apt-get install tesseract-ocr`
  - macOS: `brew install tesseract`
  - Windows: Download from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
- **Python package**: `pip install pytesseract`

### EasyOCR

- **Installation**: `pip install easyocr`
- **Features**: GPU support, 80+ languages, deep learning-based

### PaddleOCR

- **Installation**: `pip install paddleocr`
- **Features**: High accuracy, multilingual, lightweight models

## Image Preprocessing

MatOCR8D includes advanced image preprocessing to improve OCR accuracy:

```python
from matocr8d.preprocessing import ImagePreprocessor

preprocessor = ImagePreprocessor()

# Apply comprehensive enhancement
enhanced_image = preprocessor.enhance_for_ocr("image.jpg")

# Deskew image
deskewed_image = preprocessor.deskew("scanned_document.jpg")

# Custom preprocessing operations
processed_image = preprocessor.process(
    "image.jpg",
    operations=['grayscale', 'noise_reduction', 'contrast_enhancement']
)
```

## Supported Languages

Different engines support different languages:

### Tesseract
- English, Chinese, Japanese, Korean, Arabic, Russian, German, French, Spanish, Italian, and many more

### EasyOCR  
- 80+ languages including English, Chinese (Simplified/Traditional), Japanese, Korean, Arabic, Hindi, and more

### PaddleOCR
- Chinese, English, Japanese, Korean, French, German, Spanish, and more

## API Reference

### MatOCR8D Class

```python
class MatOCR8D:
    def __init__(self, 
                 engine: str = "tesseract",
                 language: Union[str, List[str]] = "eng",
                 preprocessing: bool = True,
                 confidence_threshold: float = 0.5,
                 **kwargs):
        """Initialize OCR engine"""
    
    def extract_text(self, 
                    image_path: Union[str, Path],
                    preprocess: Optional[bool] = None,
                    return_confidence: bool = False,
                    return_details: bool = False) -> Union[str, Dict]:
        """Extract text from image"""
    
    def extract_text_batch(self, 
                          image_paths: List[Union[str, Path]],
                          **kwargs) -> List[Union[str, Dict]]:
        """Extract text from multiple images"""
```

## Examples

### Document Processing

```python
from matocr8d import MatOCR8D

# Initialize for document processing
ocr = MatOCR8D(
    engine="tesseract",
    language="eng",
    preprocessing=True,
    confidence_threshold=0.8
)

# Process a document
document_text = ocr.extract_text("contract.pdf")
print("Contract text:", document_text)
```

### Multilingual Text Extraction

```python
# Extract text from multilingual document
ocr = MatOCR8D(engine="easyocr", language=["en", "fr", "de"])
result = ocr.extract_text("multilingual_doc.jpg", return_details=True)

for word_info in result['results']:
    print(f"Text: {word_info['text']}")
    print(f"Confidence: {word_info['confidence']}")
    print(f"Position: {word_info['bbox']}")
```

### Receipt Processing

```python
# Process receipt with custom preprocessing
ocr = MatOCR8D(engine="paddleocr", preprocessing=True)
result = ocr.extract_text("receipt.jpg", return_details=True)

# Filter high-confidence text
high_confidence_text = [
    item['text'] for item in result['results'] 
    if item['confidence'] > 0.9
]
print("High confidence text:", high_confidence_text)
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/yourusername/matocr8d.git
cd matocr8d
pip install -e .[dev]
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black matocr8d/
flake8 matocr8d/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

## Support

- **Documentation**: [https://matocr8d.readthedocs.io/](https://matocr8d.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/matocr8d/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/matocr8d/discussions)

## Citation

If you use MatOCR8D in your research, please cite:

```bibtex
@software{matocr8d,
  title={MatOCR8D: Advanced OCR Library for Python},
  author={MatOCR8D Team},
  year={2024},
  url={https://github.com/yourusername/matocr8d}
}
```

---

**MatOCR8D** - Making OCR simple and powerful! 🚀
