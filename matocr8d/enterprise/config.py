"""
Enterprise configuration management
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    name: str = "matocr8d"
    username: str = "postgres"
    password: str = ""
    ssl_mode: str = "require"
    pool_size: int = 10
    max_overflow: int = 20


@dataclass
class RedisConfig:
    """Redis configuration for caching and sessions"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ssl: bool = True
    connection_pool_size: int = 50


@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str = ""
    jwt_expiry_hours: int = 24
    api_key_length: int = 32
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    encryption_key: Optional[str] = None
    allowed_origins: list = field(default_factory=lambda: ["*"])
    require_https: bool = True


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    requests_per_minute: int = 100
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_size: int = 10
    enable_redis_backend: bool = True


@dataclass
class MonitoringConfig:
    """Monitoring and analytics configuration"""
    enable_metrics: bool = True
    metrics_backend: str = "prometheus"
    enable_tracing: bool = True
    tracing_backend: str = "jaeger"
    log_level: LogLevel = LogLevel.INFO
    enable_audit_logs: bool = True
    retention_days: int = 30


@dataclass
class OCRConfig:
    """OCR engine configuration"""
    default_engine: str = "tesseract"
    max_file_size_mb: int = 50
    supported_formats: list = field(default_factory=lambda: [
        ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp", ".pdf"
    ])
    timeout_seconds: int = 30
    max_concurrent_jobs: int = 10
    enable_gpu: bool = False


@dataclass
class EnterpriseConfig:
    """Main enterprise configuration"""
    
    # Environment
    environment: Environment = Environment.PRODUCTION
    debug: bool = False
    
    # Service configuration
    service_name: str = "matocr8d-enterprise"
    version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Sub-configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    ocr: OCRConfig = field(default_factory=OCRConfig)
    
    # Feature flags
    enable_api: bool = True
    enable_webhook: bool = False
    enable_batch_processing: bool = True
    enable_real_time_processing: bool = False
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> 'EnterpriseConfig':
        """Load configuration from file (JSON or YAML)"""
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnterpriseConfig':
        """Create configuration from dictionary"""
        # Handle nested configurations
        if 'database' in data:
            data['database'] = DatabaseConfig(**data['database'])
        
        if 'redis' in data:
            data['redis'] = RedisConfig(**data['redis'])
        
        if 'security' in data:
            data['security'] = SecurityConfig(**data['security'])
        
        if 'rate_limit' in data:
            data['rate_limit'] = RateLimitConfig(**data['rate_limit'])
        
        if 'monitoring' in data:
            data['monitoring'] = MonitoringConfig(**data['monitoring'])
        
        if 'ocr' in data:
            data['ocr'] = OCRConfig(**data['ocr'])
        
        # Handle enum types
        if 'environment' in data:
            data['environment'] = Environment(data['environment'])
        
        if 'monitoring' in data and 'log_level' in data['monitoring']:
            data['monitoring'].log_level = LogLevel(data['monitoring']['log_level'])
        
        return cls(**data)
    
    @classmethod
    def from_env(cls) -> 'EnterpriseConfig':
        """Load configuration from environment variables"""
        config = cls()
        
        # Environment
        if os.getenv('MATOCR8D_ENV'):
            config.environment = Environment(os.getenv('MATOCR8D_ENV'))
        
        config.debug = os.getenv('MATOCR8D_DEBUG', 'false').lower() == 'true'
        config.host = os.getenv('MATOCR8D_HOST', config.host)
        config.port = int(os.getenv('MATOCR8D_PORT', config.port))
        
        # Database
        config.database.host = os.getenv('DB_HOST', config.database.host)
        config.database.port = int(os.getenv('DB_PORT', config.database.port))
        config.database.name = os.getenv('DB_NAME', config.database.name)
        config.database.username = os.getenv('DB_USERNAME', config.database.username)
        config.database.password = os.getenv('DB_PASSWORD', config.database.password)
        
        # Redis
        config.redis.host = os.getenv('REDIS_HOST', config.redis.host)
        config.redis.port = int(os.getenv('REDIS_PORT', config.redis.port))
        config.redis.password = os.getenv('REDIS_PASSWORD', config.redis.password)
        
        # Security
        config.security.secret_key = os.getenv('SECRET_KEY', config.security.secret_key)
        config.security.encryption_key = os.getenv('ENCRYPTION_KEY', config.security.encryption_key)
        
        # OCR
        config.ocr.default_engine = os.getenv('OCR_DEFAULT_ENGINE', config.ocr.default_engine)
        config.ocr.max_file_size_mb = int(os.getenv('OCR_MAX_FILE_SIZE_MB', config.ocr.max_file_size_mb))
        config.ocr.enable_gpu = os.getenv('OCR_ENABLE_GPU', 'false').lower() == 'true'
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        result = {}
        
        for key, value in self.__dict__.items():
            if hasattr(value, '__dict__'):
                # Handle nested dataclasses
                result[key] = value.__dict__.copy()
            elif isinstance(value, Enum):
                result[key] = value.value
            else:
                result[key] = value
        
        return result
    
    def save_to_file(self, config_path: Union[str, Path], format: str = "yaml"):
        """Save configuration to file"""
        config_path = Path(config_path)
        data = self.to_dict()
        
        with open(config_path, 'w') as f:
            if format.lower() == 'yaml':
                yaml.dump(data, f, default_flow_style=False, indent=2)
            else:
                json.dump(data, f, indent=2)
    
    def validate(self) -> bool:
        """Validate configuration"""
        errors = []
        
        # Check required fields
        if not self.security.secret_key:
            errors.append("Security secret key is required")
        
        if not self.database.password:
            errors.append("Database password is required")
        
        # Check port ranges
        if not (1 <= self.port <= 65535):
            errors.append("Port must be between 1 and 65535")
        
        if errors:
            raise ValueError("Configuration validation failed: " + "; ".join(errors))
        
        return True
