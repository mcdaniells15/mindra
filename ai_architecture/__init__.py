"""
AI Architecture package initialization.
This makes the directory a proper Python package.
"""

__version__ = "0.1.0"

from .exceptions import DocumentProcessingError, APIError
from .utils import DocumentProcessor

__all__ = [
    'DocumentProcessor',
    'DocumentProcessingError',
    'APIError'
]