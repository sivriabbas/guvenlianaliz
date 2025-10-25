"""
Phase 8.F: Advanced Security Features - JWT Token Manager
JWT token creation, validation, and encryption
"""

import jwt
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from pathlib import Path
import json

class JWTManager:
    """JWT token creation and validation manager"""
    
    def __init__(
        self,
        secret_key: str = None,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 30
    ):
        self.secret_key = secret_key or self._generate_secret_key()
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        
        # Token blacklist (in production, use Redis or database)
        self.blacklist = set()
    
    def create_access_token(
        self,
        subject: str,
        additional_claims: Dict[str, Any] = None,
        expires_delta: timedelta = None
    ) -> str:
        """Create JWT access token"""
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.access_token_expire_minutes)
        
        expire = datetime.utcnow() + expires_delta
        
        # Standard JWT claims
        payload = {
            "sub": subject,  # Subject (user identifier)
            "exp": expire,   # Expiration time
            "iat": datetime.utcnow(),  # Issued at
            "type": "access"
        }
        
        # Add additional claims
        if additional_claims:
            payload.update(additional_claims)
        
        # Encode token
        encoded_jwt = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(
        self,
        subject: str,
        additional_claims: Dict[str, Any] = None,
        expires_delta: timedelta = None
    ) -> str:
        """Create JWT refresh token"""
        if expires_delta is None:
            expires_delta = timedelta(days=self.refresh_token_expire_days)
        
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": secrets.token_urlsafe(16)  # JWT ID for tracking
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        encoded_jwt = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_token_pair(
        self,
        subject: str,
        additional_claims: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """Create both access and refresh tokens"""
        access_token = self.create_access_token(subject, additional_claims)
        refresh_token = self.create_refresh_token(subject, additional_claims)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": self.access_token_expire_minutes * 60
        }
    
    def verify_token(
        self,
        token: str,
        expected_type: str = None
    ) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            # Check if token is blacklisted
            if self._is_blacklisted(token):
                return None
            
            # Decode and verify token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            # Verify token type if specified
            if expected_type and payload.get("type") != expected_type:
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            # Token has expired
            return None
        except jwt.InvalidTokenError:
            # Invalid token
            return None
        except Exception:
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Create new access token from refresh token"""
        # Verify refresh token
        payload = self.verify_token(refresh_token, expected_type="refresh")
        
        if not payload:
            return None
        
        # Extract subject and claims (excluding standard claims)
        subject = payload["sub"]
        additional_claims = {
            k: v for k, v in payload.items()
            if k not in ["sub", "exp", "iat", "type", "jti"]
        }
        
        # Create new access token
        access_token = self.create_access_token(subject, additional_claims)
        
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": self.access_token_expire_minutes * 60
        }
    
    def revoke_token(self, token: str) -> bool:
        """Revoke token by adding to blacklist"""
        try:
            # Decode to get JTI or token hash
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False}  # Don't verify expiration
            )
            
            # Use JTI if available, otherwise hash the token
            token_id = payload.get("jti", self._hash_token(token))
            self.blacklist.add(token_id)
            
            return True
        except Exception:
            return False
    
    def decode_without_verification(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode token without verification (for debugging)"""
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False}
            )
            return payload
        except Exception:
            return None
    
    def get_token_claims(self, token: str) -> Optional[Dict[str, Any]]:
        """Get token claims (verified)"""
        return self.verify_token(token)
    
    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired"""
        try:
            jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return False
        except jwt.ExpiredSignatureError:
            return True
        except Exception:
            return True
    
    def get_token_expiration(self, token: str) -> Optional[datetime]:
        """Get token expiration time"""
        payload = self.decode_without_verification(token)
        if payload and "exp" in payload:
            return datetime.fromtimestamp(payload["exp"])
        return None
    
    def get_token_subject(self, token: str) -> Optional[str]:
        """Get token subject (user ID)"""
        payload = self.verify_token(token)
        if payload:
            return payload.get("sub")
        return None
    
    def _generate_secret_key(self) -> str:
        """Generate secure secret key"""
        return secrets.token_urlsafe(64)
    
    def _hash_token(self, token: str) -> str:
        """Hash token for blacklist storage"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def _is_blacklisted(self, token: str) -> bool:
        """Check if token is in blacklist"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )
            
            token_id = payload.get("jti", self._hash_token(token))
            return token_id in self.blacklist
        except Exception:
            return False


class JWTManagerRSA:
    """JWT manager with RSA asymmetric encryption"""
    
    def __init__(
        self,
        private_key_path: str = None,
        public_key_path: str = None,
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 30
    ):
        self.algorithm = "RS256"
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        
        # Load or generate keys
        if private_key_path and public_key_path:
            self.private_key = self._load_key(private_key_path)
            self.public_key = self._load_key(public_key_path)
        else:
            self.private_key, self.public_key = self._generate_rsa_keys()
        
        self.blacklist = set()
    
    def create_access_token(
        self,
        subject: str,
        additional_claims: Dict[str, Any] = None,
        expires_delta: timedelta = None
    ) -> str:
        """Create JWT access token with RSA"""
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.access_token_expire_minutes)
        
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        encoded_jwt = jwt.encode(payload, self.private_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(
        self,
        token: str,
        expected_type: str = None
    ) -> Optional[Dict[str, Any]]:
        """Verify JWT token with RSA public key"""
        try:
            if self._is_blacklisted(token):
                return None
            
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm]
            )
            
            if expected_type and payload.get("type") != expected_type:
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None
    
    def _load_key(self, key_path: str) -> str:
        """Load RSA key from file"""
        return Path(key_path).read_text()
    
    def _generate_rsa_keys(self):
        """Generate RSA key pair (requires cryptography library)"""
        try:
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.backends import default_backend
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            # Serialize private key
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            # Generate public key
            public_key = private_key.public_key()
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            return private_pem.decode(), public_pem.decode()
            
        except ImportError:
            raise ImportError("cryptography library required for RSA keys")
    
    def _hash_token(self, token: str) -> str:
        """Hash token for blacklist"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def _is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        try:
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )
            
            token_id = payload.get("jti", self._hash_token(token))
            return token_id in self.blacklist
        except Exception:
            return False


# Test code
if __name__ == "__main__":
    print("🔐 Testing JWT Manager...")
    
    jwt_manager = JWTManager()
    
    # Create token pair
    print("\n🎫 Creating token pair...")
    tokens = jwt_manager.create_token_pair(
        subject="user123",
        additional_claims={
            "email": "user@example.com",
            "role": "admin",
            "permissions": ["read", "write", "delete"]
        }
    )
    
    print(f"Access Token: {tokens['access_token'][:50]}...")
    print(f"Refresh Token: {tokens['refresh_token'][:50]}...")
    print(f"Token Type: {tokens['token_type']}")
    print(f"Expires in: {tokens['expires_in']} seconds")
    
    # Verify access token
    print("\n✅ Verifying access token...")
    payload = jwt_manager.verify_token(tokens['access_token'], expected_type="access")
    if payload:
        print(f"Subject: {payload['sub']}")
        print(f"Email: {payload['email']}")
        print(f"Role: {payload['role']}")
        print(f"Permissions: {payload['permissions']}")
        print("✅ Token is valid!")
    
    # Get token expiration
    print("\n⏰ Token expiration...")
    expiration = jwt_manager.get_token_expiration(tokens['access_token'])
    print(f"Expires at: {expiration}")
    
    # Refresh access token
    print("\n🔄 Refreshing access token...")
    new_tokens = jwt_manager.refresh_access_token(tokens['refresh_token'])
    if new_tokens:
        print(f"New Access Token: {new_tokens['access_token'][:50]}...")
        print("✅ Token refreshed successfully!")
    
    # Revoke token
    print("\n🚫 Revoking access token...")
    jwt_manager.revoke_token(tokens['access_token'])
    
    # Try to verify revoked token
    print("\n❌ Verifying revoked token...")
    payload = jwt_manager.verify_token(tokens['access_token'])
    if payload is None:
        print("✅ Revoked token rejected successfully!")
    
    print("\n✅ JWT Manager test complete!")
