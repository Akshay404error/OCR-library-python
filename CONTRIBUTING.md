# Contributing to MatOCR8D

Thank you for your interest in contributing to MatOCR8D! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic knowledge of OCR concepts

### Development Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/yourusername/matocr8d.git
   cd matocr8d
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**
   ```bash
   pip install -e .[dev]
   ```

4. **Install OCR engines (optional)**
   ```bash
   # Install all OCR engines for testing
   pip install -e .[all]
   
   # Or install specific engines
   pip install pytesseract  # For Tesseract
   pip install easyocr      # For EasyOCR
   pip install paddleocr    # For PaddleOCR
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 2. Make Changes

- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=matocr8d

# Run specific test file
pytest tests/test_core.py
```

### 4. Code Quality Checks

```bash
# Linting
flake8 matocr8d tests

# Type checking
mypy matocr8d

# Formatting
black matocr8d tests
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new OCR engine support"
```

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

## Code Style

We use several tools to maintain code quality:

- **Black**: Code formatting (line length: 88)
- **Flake8**: Linting
- **MyPy**: Type checking
- **pytest**: Testing

### Naming Conventions

- Classes: `PascalCase`
- Functions and variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_leading_underscore`

### Documentation

- Use docstrings for all public functions and classes
- Follow Google-style docstrings
- Include type hints where possible

```python
def extract_text(self, image_path: str) -> str:
    """Extract text from an image.
    
    Args:
        image_path: Path to the image file.
        
    Returns:
        Extracted text as a string.
        
    Raises:
        FileNotFoundError: If the image file doesn't exist.
    """
    pass
```

## Testing

### Test Structure

```
tests/
├── test_core.py          # Core functionality tests
├── test_engines.py       # OCR engine tests
├── test_preprocessing.py # Preprocessing tests
├── test_utils.py         # Utility function tests
└── fixtures/             # Test images and data
```

### Writing Tests

- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies when appropriate
- Use fixtures for common test data

```python
def test_extract_text_with_valid_image(self):
    """Test text extraction with a valid image file."""
    # Arrange
    ocr = MatOCR8D()
    test_image = "fixtures/test_image.jpg"
    
    # Act
    result = ocr.extract_text(test_image)
    
    # Assert
    self.assertIsInstance(result, str)
    self.assertTrue(len(result) > 0)
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_core.py::TestMatOCR8D::test_extract_text

# Run with coverage
pytest --cov=matocr8d --cov-report=html
```

## Adding New OCR Engines

### 1. Create Engine Class

Create a new file in `matocr8d/engines/`:

```python
# matocr8d/engines/new_engine.py
from .base import OCREngine

class NewOCREngine(OCREngine):
    def __init__(self, language="eng", **kwargs):
        super().__init__(language, **kwargs)
        # Initialize your OCR engine
    
    def extract_text(self, image_path):
        # Implement text extraction
        pass
    
    def get_supported_languages(self):
        # Return list of supported languages
        pass
    
    def get_version(self):
        # Return engine version
        pass
```

### 2. Update Imports

Add to `matocr8d/engines/__init__.py`:

```python
from .new_engine import NewOCREngine
```

### 3. Update Core Class

Add to `matocr8d/core.py`:

```python
from .engines import NewOCREngine

# In _initialize_engine method:
engines = {
    "tesseract": TesseractEngine,
    "easyocr": EasyOCREngine,
    "paddleocr": PaddleOCREngine,
    "new_engine": NewOCREngine  # Add this
}
```

### 4. Add Tests

Create tests in `tests/test_engines.py`:

```python
def test_new_engine_initialization(self):
    """Test NewOCREngine initialization."""
    engine = NewOCREngine(language="en")
    self.assertEqual(engine.language, "en")
```

### 5. Update Documentation

- Add engine to README.md
- Update installation instructions
- Add examples

## Bug Reports

When reporting bugs, please include:

1. **Environment**: Python version, OS, OCR engine versions
2. **Steps to reproduce**: Minimal code example
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Error messages**: Full traceback if available

## Feature Requests

1. Check existing issues first
2. Use the feature request template
3. Provide clear description of the feature
4. Explain the use case
5. Consider implementation complexity

## Release Process

Releases are managed by maintainers:

1. Update version in `matocr8d/__init__.py`
2. Update `CHANGELOG.md`
3. Create Git tag
4. Build and publish to PyPI

## Community Guidelines

- Be respectful and inclusive
- Welcome newcomers
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Help

- **Documentation**: [https://matocr8d.readthedocs.io/](https://matocr8d.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/matocr8d/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/matocr8d/discussions)

## License

By contributing to MatOCR8D, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to MatOCR8D! 🚀
