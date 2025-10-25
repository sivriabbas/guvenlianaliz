"""
Phase 8.F: Advanced Security Features - OAuth2 Authentication
OAuth2 authorization code flow with PKCE, token management
"""

import secrets
import hashlib
import base64
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path
import sqlite3

class OAuth2Manager:
    """OAuth2 authentication and authorization manager"""
    
    def __init__(self, db_path: str = "oauth2.db"):
        self.db_path = Path(db_path)
        self.ensure_tables()
        
        # OAuth2 configuration
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 30
        self.authorization_code_expire_minutes = 10
    
    def ensure_tables(self):
        """Create OAuth2 tables"""
        with sqlite3.connect(self.db_path) as conn:
            # OAuth2 clients table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS oauth2_clients (
                    client_id TEXT PRIMARY KEY,
                    client_secret TEXT NOT NULL,
                    client_name TEXT NOT NULL,
                    redirect_uris TEXT NOT NULL,
                    grant_types TEXT NOT NULL,
                    response_types TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            """)
            
            # Authorization codes table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS authorization_codes (
                    code TEXT PRIMARY KEY,
                    client_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    redirect_uri TEXT NOT NULL,
                    scope TEXT,
                    code_challenge TEXT,
                    code_challenge_method TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_used INTEGER DEFAULT 0,
                    FOREIGN KEY (client_id) REFERENCES oauth2_clients(client_id)
                )
            """)
            
            # Access tokens table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS access_tokens (
                    token TEXT PRIMARY KEY,
                    client_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    scope TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_revoked INTEGER DEFAULT 0,
                    FOREIGN KEY (client_id) REFERENCES oauth2_clients(client_id)
                )
            """)
            
            # Refresh tokens table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS refresh_tokens (
                    token TEXT PRIMARY KEY,
                    access_token TEXT NOT NULL,
                    client_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    scope TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_revoked INTEGER DEFAULT 0,
                    FOREIGN KEY (client_id) REFERENCES oauth2_clients(client_id),
                    FOREIGN KEY (access_token) REFERENCES access_tokens(token)
                )
            """)
            
            conn.commit()
    
    def register_client(
        self,
        client_name: str,
        redirect_uris: List[str],
        grant_types: List[str] = None,
        response_types: List[str] = None
    ) -> Dict:
        """Register a new OAuth2 client"""
        if grant_types is None:
            grant_types = ["authorization_code", "refresh_token"]
        if response_types is None:
            response_types = ["code"]
        
        # Generate client credentials
        client_id = self._generate_token(32)
        client_secret = self._generate_token(64)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO oauth2_clients 
                    (client_id, client_secret, client_name, redirect_uris, grant_types, response_types)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    client_id,
                    client_secret,
                    client_name,
                    json.dumps(redirect_uris),
                    json.dumps(grant_types),
                    json.dumps(response_types)
                ))
                conn.commit()
            
            return {
                "client_id": client_id,
                "client_secret": client_secret,
                "client_name": client_name,
                "redirect_uris": redirect_uris,
                "grant_types": grant_types,
                "response_types": response_types
            }
        except Exception as e:
            return {"error": str(e)}
    
    def validate_client(self, client_id: str, client_secret: str = None) -> bool:
        """Validate OAuth2 client credentials"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if client_secret:
                    result = conn.execute("""
                        SELECT * FROM oauth2_clients 
                        WHERE client_id = ? AND client_secret = ? AND is_active = 1
                    """, (client_id, client_secret)).fetchone()
                else:
                    result = conn.execute("""
                        SELECT * FROM oauth2_clients 
                        WHERE client_id = ? AND is_active = 1
                    """, (client_id,)).fetchone()
                
                return result is not None
        except Exception as e:
            return False
    
    def create_authorization_code(
        self,
        client_id: str,
        user_id: str,
        redirect_uri: str,
        scope: str = None,
        code_challenge: str = None,
        code_challenge_method: str = "S256"
    ) -> Dict:
        """Create authorization code (PKCE support)"""
        # Validate client
        if not self.validate_client(client_id):
            return {"error": "Invalid client"}
        
        # Generate authorization code
        code = self._generate_token(32)
        expires_at = datetime.now() + timedelta(minutes=self.authorization_code_expire_minutes)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO authorization_codes 
                    (code, client_id, user_id, redirect_uri, scope, 
                     code_challenge, code_challenge_method, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    code, client_id, user_id, redirect_uri, scope,
                    code_challenge, code_challenge_method, expires_at
                ))
                conn.commit()
            
            return {
                "code": code,
                "expires_in": self.authorization_code_expire_minutes * 60
            }
        except Exception as e:
            return {"error": str(e)}
    
    def exchange_code_for_token(
        self,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        code_verifier: str = None
    ) -> Dict:
        """Exchange authorization code for access token"""
        # Validate client
        if not self.validate_client(client_id, client_secret):
            return {"error": "Invalid client credentials"}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Get authorization code
                auth_code = conn.execute("""
                    SELECT * FROM authorization_codes 
                    WHERE code = ? AND client_id = ? AND redirect_uri = ? 
                    AND is_used = 0 AND expires_at > ?
                """, (code, client_id, redirect_uri, datetime.now())).fetchone()
                
                if not auth_code:
                    return {"error": "Invalid or expired authorization code"}
                
                # Validate PKCE if used
                if auth_code['code_challenge']:
                    if not code_verifier:
                        return {"error": "Code verifier required"}
                    
                    if not self._verify_code_challenge(
                        code_verifier,
                        auth_code['code_challenge'],
                        auth_code['code_challenge_method']
                    ):
                        return {"error": "Invalid code verifier"}
                
                # Mark code as used
                conn.execute("""
                    UPDATE authorization_codes SET is_used = 1 
                    WHERE code = ?
                """, (code,))
                
                # Create access token
                access_token = self._generate_token(64)
                access_expires_at = datetime.now() + timedelta(minutes=self.access_token_expire_minutes)
                
                conn.execute("""
                    INSERT INTO access_tokens 
                    (token, client_id, user_id, scope, expires_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    access_token,
                    auth_code['client_id'],
                    auth_code['user_id'],
                    auth_code['scope'],
                    access_expires_at
                ))
                
                # Create refresh token
                refresh_token = self._generate_token(64)
                refresh_expires_at = datetime.now() + timedelta(days=self.refresh_token_expire_days)
                
                conn.execute("""
                    INSERT INTO refresh_tokens 
                    (token, access_token, client_id, user_id, scope, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    refresh_token,
                    access_token,
                    auth_code['client_id'],
                    auth_code['user_id'],
                    auth_code['scope'],
                    refresh_expires_at
                ))
                
                conn.commit()
            
            return {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": self.access_token_expire_minutes * 60,
                "refresh_token": refresh_token,
                "scope": auth_code['scope']
            }
        except Exception as e:
            return {"error": str(e)}
    
    def refresh_access_token(
        self,
        refresh_token: str,
        client_id: str,
        client_secret: str
    ) -> Dict:
        """Refresh access token using refresh token"""
        # Validate client
        if not self.validate_client(client_id, client_secret):
            return {"error": "Invalid client credentials"}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Get refresh token
                rt = conn.execute("""
                    SELECT * FROM refresh_tokens 
                    WHERE token = ? AND client_id = ? 
                    AND is_revoked = 0 AND expires_at > ?
                """, (refresh_token, client_id, datetime.now())).fetchone()
                
                if not rt:
                    return {"error": "Invalid or expired refresh token"}
                
                # Revoke old access token
                conn.execute("""
                    UPDATE access_tokens SET is_revoked = 1 
                    WHERE token = ?
                """, (rt['access_token'],))
                
                # Create new access token
                new_access_token = self._generate_token(64)
                access_expires_at = datetime.now() + timedelta(minutes=self.access_token_expire_minutes)
                
                conn.execute("""
                    INSERT INTO access_tokens 
                    (token, client_id, user_id, scope, expires_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    new_access_token,
                    rt['client_id'],
                    rt['user_id'],
                    rt['scope'],
                    access_expires_at
                ))
                
                # Update refresh token to point to new access token
                conn.execute("""
                    UPDATE refresh_tokens 
                    SET access_token = ? 
                    WHERE token = ?
                """, (new_access_token, refresh_token))
                
                conn.commit()
            
            return {
                "access_token": new_access_token,
                "token_type": "Bearer",
                "expires_in": self.access_token_expire_minutes * 60,
                "scope": rt['scope']
            }
        except Exception as e:
            return {"error": str(e)}
    
    def validate_access_token(self, token: str) -> Optional[Dict]:
        """Validate access token and return token info"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                result = conn.execute("""
                    SELECT * FROM access_tokens 
                    WHERE token = ? AND is_revoked = 0 AND expires_at > ?
                """, (token, datetime.now())).fetchone()
                
                if not result:
                    return None
                
                return {
                    "user_id": result['user_id'],
                    "client_id": result['client_id'],
                    "scope": result['scope'],
                    "expires_at": result['expires_at']
                }
        except Exception as e:
            return None
    
    def revoke_token(self, token: str, token_type: str = "access_token") -> bool:
        """Revoke access or refresh token"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if token_type == "access_token":
                    conn.execute("""
                        UPDATE access_tokens SET is_revoked = 1 
                        WHERE token = ?
                    """, (token,))
                elif token_type == "refresh_token":
                    conn.execute("""
                        UPDATE refresh_tokens SET is_revoked = 1 
                        WHERE token = ?
                    """, (token,))
                    
                    # Also revoke associated access token
                    conn.execute("""
                        UPDATE access_tokens SET is_revoked = 1 
                        WHERE token = (
                            SELECT access_token FROM refresh_tokens 
                            WHERE token = ?
                        )
                    """, (token,))
                
                conn.commit()
                return True
        except Exception as e:
            return False
    
    def get_client_info(self, client_id: str) -> Optional[Dict]:
        """Get OAuth2 client information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                result = conn.execute("""
                    SELECT client_id, client_name, redirect_uris, 
                           grant_types, response_types, created_at, is_active
                    FROM oauth2_clients 
                    WHERE client_id = ?
                """, (client_id,)).fetchone()
                
                if not result:
                    return None
                
                return {
                    "client_id": result['client_id'],
                    "client_name": result['client_name'],
                    "redirect_uris": json.loads(result['redirect_uris']),
                    "grant_types": json.loads(result['grant_types']),
                    "response_types": json.loads(result['response_types']),
                    "created_at": result['created_at'],
                    "is_active": bool(result['is_active'])
                }
        except Exception as e:
            return None
    
    def list_active_tokens(self, user_id: str) -> Dict:
        """List all active tokens for a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                access_tokens = conn.execute("""
                    SELECT token, client_id, scope, created_at, expires_at
                    FROM access_tokens 
                    WHERE user_id = ? AND is_revoked = 0 AND expires_at > ?
                    ORDER BY created_at DESC
                """, (user_id, datetime.now())).fetchall()
                
                refresh_tokens = conn.execute("""
                    SELECT token, client_id, scope, created_at, expires_at
                    FROM refresh_tokens 
                    WHERE user_id = ? AND is_revoked = 0 AND expires_at > ?
                    ORDER BY created_at DESC
                """, (user_id, datetime.now())).fetchall()
                
                return {
                    "user_id": user_id,
                    "access_tokens": [
                        {
                            "token": t['token'][:16] + "...",  # Masked
                            "client_id": t['client_id'],
                            "scope": t['scope'],
                            "created_at": t['created_at'],
                            "expires_at": t['expires_at']
                        }
                        for t in access_tokens
                    ],
                    "refresh_tokens": [
                        {
                            "token": t['token'][:16] + "...",  # Masked
                            "client_id": t['client_id'],
                            "scope": t['scope'],
                            "created_at": t['created_at'],
                            "expires_at": t['expires_at']
                        }
                        for t in refresh_tokens
                    ]
                }
        except Exception as e:
            return {"error": str(e)}
    
    def _generate_token(self, length: int = 32) -> str:
        """Generate secure random token"""
        return secrets.token_urlsafe(length)
    
    def _generate_code_challenge(self, code_verifier: str, method: str = "S256") -> str:
        """Generate PKCE code challenge"""
        if method == "S256":
            digest = hashlib.sha256(code_verifier.encode()).digest()
            return base64.urlsafe_b64encode(digest).decode().rstrip("=")
        elif method == "plain":
            return code_verifier
        else:
            raise ValueError(f"Unsupported code challenge method: {method}")
    
    def _verify_code_challenge(
        self,
        code_verifier: str,
        code_challenge: str,
        method: str = "S256"
    ) -> bool:
        """Verify PKCE code challenge"""
        try:
            expected = self._generate_code_challenge(code_verifier, method)
            return secrets.compare_digest(expected, code_challenge)
        except Exception:
            return False

# Test code
if __name__ == "__main__":
    print("🔐 Testing OAuth2 Manager...")
    
    oauth2 = OAuth2Manager()
    
    # Register client
    print("\n📝 Registering OAuth2 client...")
    client = oauth2.register_client(
        client_name="Test App",
        redirect_uris=["http://localhost:8000/callback"],
        grant_types=["authorization_code", "refresh_token"]
    )
    print(f"Client ID: {client['client_id']}")
    print(f"Client Secret: {client['client_secret'][:20]}...")
    
    # Create authorization code
    print("\n🔑 Creating authorization code...")
    auth_code = oauth2.create_authorization_code(
        client_id=client['client_id'],
        user_id="user123",
        redirect_uri="http://localhost:8000/callback",
        scope="read write"
    )
    print(f"Code: {auth_code['code'][:20]}...")
    print(f"Expires in: {auth_code['expires_in']} seconds")
    
    # Exchange code for token
    print("\n🎫 Exchanging code for token...")
    tokens = oauth2.exchange_code_for_token(
        code=auth_code['code'],
        client_id=client['client_id'],
        client_secret=client['client_secret'],
        redirect_uri="http://localhost:8000/callback"
    )
    print(f"Access Token: {tokens['access_token'][:20]}...")
    print(f"Refresh Token: {tokens['refresh_token'][:20]}...")
    print(f"Token Type: {tokens['token_type']}")
    print(f"Expires in: {tokens['expires_in']} seconds")
    
    # Validate token
    print("\n✅ Validating access token...")
    token_info = oauth2.validate_access_token(tokens['access_token'])
    if token_info:
        print(f"User ID: {token_info['user_id']}")
        print(f"Scope: {token_info['scope']}")
        print("✅ Token is valid!")
    
    # List active tokens
    print("\n📋 Listing active tokens...")
    active = oauth2.list_active_tokens("user123")
    print(f"Access tokens: {len(active['access_tokens'])}")
    print(f"Refresh tokens: {len(active['refresh_tokens'])}")
    
    print("\n✅ OAuth2 Manager test complete!")
