"""
Enterprise authentication and authorization
"""

import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

try:
    import jwt
    from passlib.context import CryptContext
    from passlib.hash import bcrypt
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

from .config import EnterpriseConfig


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    API_ONLY = "api_only"
    READ_ONLY = "read_only"


class Permission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    API_ACCESS = "api_access"
    BATCH_PROCESS = "batch_process"


@dataclass
class User:
    """User model"""
    id: str
    username: str
    email: str
    role: UserRole
    permissions: List[Permission]
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    api_keys: List[str] = None
    
    def __post_init__(self):
        if self.api_keys is None:
            self.api_keys = []


@dataclass
class APIKey:
    """API Key model"""
    key_id: str
    key_hash: str
    user_id: str
    name: str
    permissions: List[Permission]
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    is_active: bool = True
    rate_limit: Optional[int] = None


class AuthManager:
    """Enterprise authentication manager"""
    
    def __init__(self, config: EnterpriseConfig):
        if not AUTH_AVAILABLE:
            raise ImportError(
                "Authentication dependencies not found. Install with: "
                "pip install matocr8d[enterprise]"
            )
        
        self.config = config
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = config.security.secret_key
        self.algorithm = "HS256"
        
        # In-memory storage (replace with database in production)
        self.users: Dict[str, User] = {}
        self.api_keys: Dict[str, APIKey] = {}
        self.failed_attempts: Dict[str, List[datetime]] = {}
        
        # Initialize default admin user
        self._init_default_admin()
    
    def _init_default_admin(self):
        """Initialize default admin user"""
        admin_user = User(
            id="admin",
            username="admin",
            email="admin@matocr8d.com",
            role=UserRole.ADMIN,
            permissions=list(Permission),
            created_at=datetime.utcnow()
        )
        
        # Set default password (change in production)
        admin_user.password_hash = self.hash_password("admin123")
        self.users["admin"] = admin_user
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(password, hashed)
    
    def create_user(self, username: str, email: str, password: str, 
                   role: UserRole = UserRole.USER) -> User:
        """Create a new user"""
        user_id = hashlib.sha256(f"{username}{email}{time.time()}".encode()).hexdigest()
        
        permissions = self._get_default_permissions(role)
        
        user = User(
            id=user_id,
            username=username,
            email=email,
            role=role,
            permissions=permissions,
            created_at=datetime.utcnow()
        )
        
        user.password_hash = self.hash_password(password)
        self.users[user_id] = user
        
        return user
    
    def _get_default_permissions(self, role: UserRole) -> List[Permission]:
        """Get default permissions for role"""
        role_permissions = {
            UserRole.ADMIN: list(Permission),
            UserRole.USER: [Permission.READ, Permission.WRITE, Permission.API_ACCESS],
            UserRole.API_ONLY: [Permission.READ, Permission.API_ACCESS],
            UserRole.READ_ONLY: [Permission.READ]
        }
        return role_permissions.get(role, [])
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        # Check for lockout
        if self._is_locked_out(username):
            return None
        
        # Find user
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break
        
        if not user or not user.is_active:
            self._record_failed_attempt(username)
            return None
        
        # Verify password
        if not hasattr(user, 'password_hash'):
            self._record_failed_attempt(username)
            return None
        
        if not self.verify_password(password, user.password_hash):
            self._record_failed_attempt(username)
            return None
        
        # Clear failed attempts and update last login
        self._clear_failed_attempts(username)
        user.last_login = datetime.utcnow()
        
        return user
    
    def _is_locked_out(self, username: str) -> bool:
        """Check if user is locked out due to failed attempts"""
        if username not in self.failed_attempts:
            return False
        
        attempts = self.failed_attempts[username]
        recent_attempts = [
            attempt for attempt in attempts
            if attempt > datetime.utcnow() - timedelta(minutes=self.config.security.lockout_duration_minutes)
        ]
        
        return len(recent_attempts) >= self.config.security.max_login_attempts
    
    def _record_failed_attempt(self, username: str):
        """Record a failed login attempt"""
        if username not in self.failed_attempts:
            self.failed_attempts[username] = []
        
        self.failed_attempts[username].append(datetime.utcnow())
    
    def _clear_failed_attempts(self, username: str):
        """Clear failed login attempts"""
        if username in self.failed_attempts:
            del self.failed_attempts[username]
    
    def create_access_token(self, user: User, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        if expires_delta is None:
            expires_delta = timedelta(hours=self.config.security.jwt_expiry_hours)
        
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            "sub": user.id,
            "username": user.username,
            "role": user.role.value,
            "permissions": [p.value for p in user.permissions],
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_user_from_token(self, token: str) -> Optional[User]:
        """Get user from JWT token"""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        return self.users.get(user_id)
    
    def has_permission(self, user: User, permission: Permission) -> bool:
        """Check if user has specific permission"""
        return permission in user.permissions
    
    def require_permission(self, user: User, permission: Permission):
        """Require user to have specific permission"""
        if not self.has_permission(user, permission):
            raise PermissionError(f"User {user.username} lacks permission {permission.value}")


class APIKeyManager:
    """API Key management for enterprise"""
    
    def __init__(self, config: EnterpriseConfig):
        self.config = config
        self.api_keys: Dict[str, APIKey] = {}
    
    def generate_api_key(self, length: int = None) -> str:
        """Generate a new API key"""
        if length is None:
            length = self.config.security.api_key_length
        
        return secrets.token_urlsafe(length)
    
    def create_api_key(self, user_id: str, name: str, 
                      permissions: List[Permission] = None,
                      expires_at: Optional[datetime] = None,
                      rate_limit: Optional[int] = None) -> tuple[str, str]:
        """Create a new API key"""
        key_id = hashlib.sha256(f"{user_id}{name}{time.time()}".encode()).hexdigest()
        api_key = self.generate_api_key()
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        if permissions is None:
            permissions = [Permission.READ, Permission.API_ACCESS]
        
        api_key_obj = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            user_id=user_id,
            name=name,
            permissions=permissions,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            rate_limit=rate_limit
        )
        
        self.api_keys[key_id] = api_key_obj
        
        return api_key, api_key
    
    def validate_api_key(self, api_key: str) -> Optional[APIKey]:
        """Validate API key and return key object"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        for key_obj in self.api_keys.values():
            if key_obj.key_hash == key_hash and key_obj.is_active:
                # Check expiration
                if key_obj.expires_at and key_obj.expires_at < datetime.utcnow():
                    continue
                
                # Update last used
                key_obj.last_used = datetime.utcnow()
                return key_obj
        
        return None
    
    def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key"""
        if key_id in self.api_keys:
            self.api_keys[key_id].is_active = False
            return True
        return False
    
    def get_user_api_keys(self, user_id: str) -> List[APIKey]:
        """Get all API keys for a user"""
        return [key for key in self.api_keys.values() if key.user_id == user_id]
    
    def update_api_key(self, key_id: str, **kwargs) -> bool:
        """Update API key properties"""
        if key_id not in self.api_keys:
            return False
        
        key_obj = self.api_keys[key_id]
        
        for key, value in kwargs.items():
            if hasattr(key_obj, key):
                setattr(key_obj, key, value)
        
        return True
