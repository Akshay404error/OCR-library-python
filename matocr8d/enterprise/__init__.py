"""
MatOCR8D Enterprise Edition

Commercial-grade OCR solution with enterprise features:
- Advanced security and authentication
- Performance monitoring and analytics
- API rate limiting and usage tracking
- Enterprise support and SLA
"""

__version__ = "1.0.0-enterprise"
__author__ = "MatOCR8D Enterprise Team"
__email__ = "enterprise@matocr8d.com"

from .api import MatOCR8DAPI
from .auth import AuthManager, APIKeyManager
from .monitoring import PerformanceMonitor, UsageTracker
from .config import EnterpriseConfig
from .security import SecurityManager

__all__ = [
    "MatOCR8DAPI",
    "AuthManager", 
    "APIKeyManager",
    "PerformanceMonitor",
    "UsageTracker", 
    "EnterpriseConfig",
    "SecurityManager"
]
