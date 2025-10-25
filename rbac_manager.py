"""
Phase 8.F: Advanced Security Features - RBAC Manager
Role-Based Access Control with permissions and decorators
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional, Set, Callable
from functools import wraps
from datetime import datetime

class RBACManager:
    """Role-Based Access Control Manager"""
    
    def __init__(self, db_path: str = "rbac.db"):
        self.db_path = Path(db_path)
        self.ensure_tables()
        self._initialize_default_roles()
    
    def ensure_tables(self):
        """Create RBAC tables"""
        with sqlite3.connect(self.db_path) as conn:
            # Roles table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS roles (
                    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role_name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    is_system INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Permissions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS permissions (
                    permission_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    permission_name TEXT UNIQUE NOT NULL,
                    resource TEXT NOT NULL,
                    action TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Role-Permission mapping
            conn.execute("""
                CREATE TABLE IF NOT EXISTS role_permissions (
                    role_id INTEGER NOT NULL,
                    permission_id INTEGER NOT NULL,
                    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (role_id, permission_id),
                    FOREIGN KEY (role_id) REFERENCES roles(role_id),
                    FOREIGN KEY (permission_id) REFERENCES permissions(permission_id)
                )
            """)
            
            # User-Role mapping
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_roles (
                    user_id TEXT NOT NULL,
                    role_id INTEGER NOT NULL,
                    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    PRIMARY KEY (user_id, role_id),
                    FOREIGN KEY (role_id) REFERENCES roles(role_id)
                )
            """)
            
            # Role hierarchy (parent-child relationships)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS role_hierarchy (
                    parent_role_id INTEGER NOT NULL,
                    child_role_id INTEGER NOT NULL,
                    PRIMARY KEY (parent_role_id, child_role_id),
                    FOREIGN KEY (parent_role_id) REFERENCES roles(role_id),
                    FOREIGN KEY (child_role_id) REFERENCES roles(role_id)
                )
            """)
            
            conn.commit()
    
    def _initialize_default_roles(self):
        """Initialize default system roles"""
        default_roles = [
            ("admin", "System Administrator - Full access", True),
            ("developer", "Developer - API access and testing", True),
            ("viewer", "Viewer - Read-only access", True),
            ("user", "Regular User - Limited access", True)
        ]
        
        default_permissions = [
            ("api.read", "api", "read", "Read API data"),
            ("api.write", "api", "write", "Write API data"),
            ("api.delete", "api", "delete", "Delete API data"),
            ("api.admin", "api", "admin", "Admin API operations"),
            ("analytics.view", "analytics", "view", "View analytics"),
            ("analytics.export", "analytics", "export", "Export analytics"),
            ("reports.generate", "reports", "generate", "Generate reports"),
            ("reports.view", "reports", "view", "View reports"),
            ("users.manage", "users", "manage", "Manage users"),
            ("roles.manage", "roles", "manage", "Manage roles"),
        ]
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Insert default roles
                for role_name, description, is_system in default_roles:
                    conn.execute("""
                        INSERT OR IGNORE INTO roles (role_name, description, is_system)
                        VALUES (?, ?, ?)
                    """, (role_name, description, is_system))
                
                # Insert default permissions
                for perm_name, resource, action, description in default_permissions:
                    conn.execute("""
                        INSERT OR IGNORE INTO permissions 
                        (permission_name, resource, action, description)
                        VALUES (?, ?, ?, ?)
                    """, (perm_name, resource, action, description))
                
                conn.commit()
                
                # Assign permissions to roles
                self._assign_default_permissions()
        except Exception as e:
            print(f"Error initializing default roles: {e}")
    
    def _assign_default_permissions(self):
        """Assign default permissions to roles"""
        role_permissions = {
            "admin": "*",  # All permissions
            "developer": [
                "api.read", "api.write", "api.delete",
                "analytics.view", "analytics.export",
                "reports.generate", "reports.view"
            ],
            "viewer": [
                "api.read", "analytics.view", "reports.view"
            ],
            "user": [
                "api.read", "reports.view"
            ]
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                for role_name, permissions in role_permissions.items():
                    # Get role ID
                    role = conn.execute(
                        "SELECT role_id FROM roles WHERE role_name = ?",
                        (role_name,)
                    ).fetchone()
                    
                    if not role:
                        continue
                    
                    role_id = role['role_id']
                    
                    if permissions == "*":
                        # Assign all permissions
                        all_perms = conn.execute(
                            "SELECT permission_id FROM permissions"
                        ).fetchall()
                        
                        for perm in all_perms:
                            conn.execute("""
                                INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
                                VALUES (?, ?)
                            """, (role_id, perm['permission_id']))
                    else:
                        # Assign specific permissions
                        for perm_name in permissions:
                            perm = conn.execute(
                                "SELECT permission_id FROM permissions WHERE permission_name = ?",
                                (perm_name,)
                            ).fetchone()
                            
                            if perm:
                                conn.execute("""
                                    INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
                                    VALUES (?, ?)
                                """, (role_id, perm['permission_id']))
                
                conn.commit()
        except Exception as e:
            print(f"Error assigning default permissions: {e}")
    
    def create_role(self, role_name: str, description: str = None) -> Dict:
        """Create a new role"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO roles (role_name, description)
                    VALUES (?, ?)
                """, (role_name, description))
                conn.commit()
            
            return {"role_name": role_name, "description": description}
        except sqlite3.IntegrityError:
            return {"error": "Role already exists"}
        except Exception as e:
            return {"error": str(e)}
    
    def create_permission(
        self,
        permission_name: str,
        resource: str,
        action: str,
        description: str = None
    ) -> Dict:
        """Create a new permission"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO permissions 
                    (permission_name, resource, action, description)
                    VALUES (?, ?, ?, ?)
                """, (permission_name, resource, action, description))
                conn.commit()
            
            return {
                "permission_name": permission_name,
                "resource": resource,
                "action": action,
                "description": description
            }
        except sqlite3.IntegrityError:
            return {"error": "Permission already exists"}
        except Exception as e:
            return {"error": str(e)}
    
    def assign_role_to_user(
        self,
        user_id: str,
        role_name: str,
        expires_at: datetime = None
    ) -> bool:
        """Assign role to user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Get role ID
                role = conn.execute(
                    "SELECT role_id FROM roles WHERE role_name = ?",
                    (role_name,)
                ).fetchone()
                
                if not role:
                    return False
                
                conn.execute("""
                    INSERT OR REPLACE INTO user_roles (user_id, role_id, expires_at)
                    VALUES (?, ?, ?)
                """, (user_id, role['role_id'], expires_at))
                conn.commit()
            
            return True
        except Exception as e:
            return False
    
    def revoke_role_from_user(self, user_id: str, role_name: str) -> bool:
        """Revoke role from user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                role = conn.execute(
                    "SELECT role_id FROM roles WHERE role_name = ?",
                    (role_name,)
                ).fetchone()
                
                if not role:
                    return False
                
                conn.execute("""
                    DELETE FROM user_roles 
                    WHERE user_id = ? AND role_id = ?
                """, (user_id, role['role_id']))
                conn.commit()
            
            return True
        except Exception:
            return False
    
    def assign_permission_to_role(
        self,
        role_name: str,
        permission_name: str
    ) -> bool:
        """Assign permission to role"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                role = conn.execute(
                    "SELECT role_id FROM roles WHERE role_name = ?",
                    (role_name,)
                ).fetchone()
                
                permission = conn.execute(
                    "SELECT permission_id FROM permissions WHERE permission_name = ?",
                    (permission_name,)
                ).fetchone()
                
                if not role or not permission:
                    return False
                
                conn.execute("""
                    INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
                    VALUES (?, ?)
                """, (role['role_id'], permission['permission_id']))
                conn.commit()
            
            return True
        except Exception:
            return False
    
    def get_user_roles(self, user_id: str) -> List[str]:
        """Get all roles assigned to user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                roles = conn.execute("""
                    SELECT r.role_name 
                    FROM user_roles ur
                    JOIN roles r ON ur.role_id = r.role_id
                    WHERE ur.user_id = ?
                    AND (ur.expires_at IS NULL OR ur.expires_at > ?)
                """, (user_id, datetime.now())).fetchall()
                
                return [role['role_name'] for role in roles]
        except Exception:
            return []
    
    def get_user_permissions(self, user_id: str) -> Set[str]:
        """Get all permissions for user (including inherited from roles)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                permissions = conn.execute("""
                    SELECT DISTINCT p.permission_name
                    FROM user_roles ur
                    JOIN role_permissions rp ON ur.role_id = rp.role_id
                    JOIN permissions p ON rp.permission_id = p.permission_id
                    WHERE ur.user_id = ?
                    AND (ur.expires_at IS NULL OR ur.expires_at > ?)
                """, (user_id, datetime.now())).fetchall()
                
                return {perm['permission_name'] for perm in permissions}
        except Exception:
            return set()
    
    def has_permission(self, user_id: str, permission_name: str) -> bool:
        """Check if user has specific permission"""
        permissions = self.get_user_permissions(user_id)
        return permission_name in permissions
    
    def has_role(self, user_id: str, role_name: str) -> bool:
        """Check if user has specific role"""
        roles = self.get_user_roles(user_id)
        return role_name in roles
    
    def has_any_role(self, user_id: str, role_names: List[str]) -> bool:
        """Check if user has any of the specified roles"""
        user_roles = self.get_user_roles(user_id)
        return any(role in user_roles for role in role_names)
    
    def has_all_roles(self, user_id: str, role_names: List[str]) -> bool:
        """Check if user has all specified roles"""
        user_roles = self.get_user_roles(user_id)
        return all(role in user_roles for role in role_names)
    
    def get_role_permissions(self, role_name: str) -> List[str]:
        """Get all permissions for a role"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                permissions = conn.execute("""
                    SELECT p.permission_name
                    FROM roles r
                    JOIN role_permissions rp ON r.role_id = rp.role_id
                    JOIN permissions p ON rp.permission_id = p.permission_id
                    WHERE r.role_name = ?
                """, (role_name,)).fetchall()
                
                return [perm['permission_name'] for perm in permissions]
        except Exception:
            return []
    
    def list_all_roles(self) -> List[Dict]:
        """List all roles"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                roles = conn.execute("""
                    SELECT role_id, role_name, description, is_system, created_at
                    FROM roles
                    ORDER BY role_name
                """).fetchall()
                
                return [
                    {
                        "role_id": r['role_id'],
                        "role_name": r['role_name'],
                        "description": r['description'],
                        "is_system": bool(r['is_system']),
                        "created_at": r['created_at']
                    }
                    for r in roles
                ]
        except Exception:
            return []
    
    def list_all_permissions(self) -> List[Dict]:
        """List all permissions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                permissions = conn.execute("""
                    SELECT permission_id, permission_name, resource, 
                           action, description, created_at
                    FROM permissions
                    ORDER BY resource, action
                """).fetchall()
                
                return [
                    {
                        "permission_id": p['permission_id'],
                        "permission_name": p['permission_name'],
                        "resource": p['resource'],
                        "action": p['action'],
                        "description": p['description'],
                        "created_at": p['created_at']
                    }
                    for p in permissions
                ]
        except Exception:
            return []


# Decorators for FastAPI/Flask
def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get user_id from kwargs or current context
            user_id = kwargs.get('user_id') or kwargs.get('current_user')
            
            if not user_id:
                raise PermissionError("User not authenticated")
            
            rbac = RBACManager()
            if not rbac.has_permission(user_id, permission):
                raise PermissionError(f"Permission '{permission}' required")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role: str):
    """Decorator to require specific role"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id') or kwargs.get('current_user')
            
            if not user_id:
                raise PermissionError("User not authenticated")
            
            rbac = RBACManager()
            if not rbac.has_role(user_id, role):
                raise PermissionError(f"Role '{role}' required")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_role(*roles: str):
    """Decorator to require any of the specified roles"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id') or kwargs.get('current_user')
            
            if not user_id:
                raise PermissionError("User not authenticated")
            
            rbac = RBACManager()
            if not rbac.has_any_role(user_id, list(roles)):
                raise PermissionError(f"One of roles {roles} required")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Test code
if __name__ == "__main__":
    print("🔐 Testing RBAC Manager...")
    
    rbac = RBACManager()
    
    # Assign role to user
    print("\n👤 Assigning admin role to user...")
    rbac.assign_role_to_user("user123", "admin")
    
    # Get user roles
    print("\n📋 User roles:")
    roles = rbac.get_user_roles("user123")
    for role in roles:
        print(f"  - {role}")
    
    # Get user permissions
    print("\n🔑 User permissions:")
    permissions = rbac.get_user_permissions("user123")
    for perm in sorted(permissions):
        print(f"  - {perm}")
    
    # Check specific permission
    print("\n✅ Permission checks:")
    print(f"  api.read: {rbac.has_permission('user123', 'api.read')}")
    print(f"  api.write: {rbac.has_permission('user123', 'api.write')}")
    print(f"  api.delete: {rbac.has_permission('user123', 'api.delete')}")
    
    # List all roles
    print("\n📊 All system roles:")
    all_roles = rbac.list_all_roles()
    for role in all_roles:
        perm_count = len(rbac.get_role_permissions(role['role_name']))
        print(f"  - {role['role_name']}: {perm_count} permissions")
    
    print("\n✅ RBAC Manager test complete!")
