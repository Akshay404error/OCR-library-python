"""
Setup script for matocr8d
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read version from __init__.py
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'matocr8d', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return "1.0.0"

setup(
    name="matocr8d",
    version=get_version(),
    author="MatOCR8D Team",
    author_email="contact@matocr8d.com",
    description="Advanced OCR library with multiple engine support and preprocessing capabilities",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/matocr8d",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing"
    ],
    python_requires=">=3.8",
    install_requires=[
        "Pillow>=9.0.0",
        "numpy>=1.21.0"
    ],
    extras_require={
        "tesseract": ["pytesseract>=0.3.10"],
        "easyocr": ["easyocr>=1.6.0"],
        "paddleocr": ["paddleocr>=2.6.0"],
        "opencv": ["opencv-python>=4.5.0"],
        "all": [
            "pytesseract>=0.3.10",
            "easyocr>=1.6.0",
            "paddleocr>=2.6.0",
            "opencv-python>=4.5.0"
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0"
        ]
    },
    keywords="ocr optical character recognition text extraction computer vision",
    project_urls={
        "Documentation": "https://matocr8d.readthedocs.io/",
        "Source": "https://github.com/yourusername/matocr8d",
        "Tracker": "https://github.com/yourusername/matocr8d/issues",
    },
    include_package_data=True,
    zip_safe=False,
)
