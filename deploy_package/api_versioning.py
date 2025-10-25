"""
Phase 8.F: Advanced Security Features - API Versioning
Multiple API versions with backward compatibility
"""

from typing import Dict, List, Optional, Callable, Any
from functools import wraps
from datetime import datetime, timedelta
import json

class APIVersion:
    """API version metadata"""
    
    def __init__(
        self,
        version: str,
        release_date: str,
        deprecated: bool = False,
        deprecation_date: str = None,
        sunset_date: str = None,
        changes: List[str] = None
    ):
        self.version = version
        self.release_date = release_date
        self.deprecated = deprecated
        self.deprecation_date = deprecation_date
        self.sunset_date = sunset_date
        self.changes = changes or []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "version": self.version,
            "release_date": self.release_date,
            "deprecated": self.deprecated,
            "deprecation_date": self.deprecation_date,
            "sunset_date": self.sunset_date,
            "changes": self.changes,
            "status": self.get_status()
        }
    
    def get_status(self) -> str:
        """Get version status"""
        if self.sunset_date:
            sunset = datetime.fromisoformat(self.sunset_date)
            if datetime.now() > sunset:
                return "sunset"
        
        if self.deprecated:
            return "deprecated"
        
        return "active"
    
    def is_active(self) -> bool:
        """Check if version is still active"""
        return self.get_status() in ["active", "deprecated"]


class APIVersionManager:
    """Manage multiple API versions with backward compatibility"""
    
    def __init__(self):
        self.versions: Dict[str, APIVersion] = {}
        self.default_version = "v1"
        self._initialize_versions()
    
    def _initialize_versions(self):
        """Initialize API versions"""
        # Version 1 - Original API
        self.register_version(
            version="v1",
            release_date="2024-01-01",
            changes=[
                "Initial API release",
                "Basic authentication",
                "Core endpoints"
            ]
        )
        
        # Version 2 - Enhanced security
        self.register_version(
            version="v2",
            release_date="2024-06-01",
            changes=[
                "OAuth2 authentication added",
                "JWT token support",
                "RBAC implementation",
                "Enhanced error handling",
                "Rate limiting improvements"
            ]
        )
        
        # Version 3 - Future version (planned)
        self.register_version(
            version="v3",
            release_date="2024-12-01",
            changes=[
                "GraphQL support planned",
                "WebSocket real-time updates",
                "Advanced analytics API",
                "Multi-tenant support"
            ]
        )
    
    def register_version(
        self,
        version: str,
        release_date: str,
        deprecated: bool = False,
        deprecation_date: str = None,
        sunset_date: str = None,
        changes: List[str] = None
    ):
        """Register new API version"""
        self.versions[version] = APIVersion(
            version=version,
            release_date=release_date,
            deprecated=deprecated,
            deprecation_date=deprecation_date,
            sunset_date=sunset_date,
            changes=changes
        )
    
    def deprecate_version(
        self,
        version: str,
        deprecation_date: str = None,
        sunset_date: str = None
    ):
        """Mark version as deprecated"""
        if version in self.versions:
            self.versions[version].deprecated = True
            self.versions[version].deprecation_date = deprecation_date or datetime.now().isoformat()
            self.versions[version].sunset_date = sunset_date
    
    def get_version(self, version: str) -> Optional[APIVersion]:
        """Get specific version"""
        return self.versions.get(version)
    
    def list_versions(self, include_sunset: bool = False) -> List[Dict]:
        """List all versions"""
        versions = []
        for v in self.versions.values():
            if include_sunset or v.is_active():
                versions.append(v.to_dict())
        
        # Sort by version number
        versions.sort(key=lambda x: x['version'], reverse=True)
        return versions
    
    def get_latest_version(self) -> str:
        """Get latest active version"""
        active_versions = [
            v.version for v in self.versions.values()
            if v.is_active()
        ]
        
        if active_versions:
            return max(active_versions)
        return self.default_version
    
    def validate_version(self, version: str) -> bool:
        """Check if version is valid and active"""
        v = self.get_version(version)
        return v is not None and v.is_active()
    
    def get_deprecation_warning(self, version: str) -> Optional[Dict]:
        """Get deprecation warning for version"""
        v = self.get_version(version)
        
        if v and v.deprecated:
            return {
                "warning": f"API version {version} is deprecated",
                "deprecation_date": v.deprecation_date,
                "sunset_date": v.sunset_date,
                "migration_guide": f"Please migrate to version {self.get_latest_version()}",
                "latest_version": self.get_latest_version()
            }
        
        return None


class VersionedEndpoint:
    """Container for versioned endpoint implementations"""
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.implementations: Dict[str, Callable] = {}
    
    def add_version(self, version: str, handler: Callable):
        """Add version implementation"""
        self.implementations[version] = handler
    
    def get_handler(self, version: str) -> Optional[Callable]:
        """Get handler for specific version"""
        return self.implementations.get(version)
    
    def has_version(self, version: str) -> bool:
        """Check if version exists"""
        return version in self.implementations


class APIVersionRouter:
    """Route requests to appropriate API version"""
    
    def __init__(self, version_manager: APIVersionManager):
        self.version_manager = version_manager
        self.endpoints: Dict[str, VersionedEndpoint] = {}
    
    def register_endpoint(
        self,
        path: str,
        version: str,
        handler: Callable
    ):
        """Register versioned endpoint"""
        if path not in self.endpoints:
            self.endpoints[path] = VersionedEndpoint(path)
        
        self.endpoints[path].add_version(version, handler)
    
    def route_request(
        self,
        path: str,
        version: str = None,
        **kwargs
    ) -> Any:
        """Route request to appropriate version handler"""
        # Use default version if not specified
        if not version:
            version = self.version_manager.default_version
        
        # Validate version
        if not self.version_manager.validate_version(version):
            raise ValueError(f"Invalid or sunset API version: {version}")
        
        # Get endpoint
        endpoint = self.endpoints.get(path)
        if not endpoint:
            raise ValueError(f"Endpoint not found: {path}")
        
        # Get version handler
        handler = endpoint.get_handler(version)
        
        # Fallback to latest version if specific version not implemented
        if not handler:
            latest_version = self.version_manager.get_latest_version()
            handler = endpoint.get_handler(latest_version)
        
        if not handler:
            raise ValueError(f"No handler found for {path} version {version}")
        
        # Get deprecation warning
        warning = self.version_manager.get_deprecation_warning(version)
        
        # Execute handler
        result = handler(**kwargs)
        
        # Add warning to response if deprecated
        if warning and isinstance(result, dict):
            result['_deprecation_warning'] = warning
        
        return result


# Decorator for versioned endpoints
def versioned(version: str):
    """Decorator to mark endpoint as version-specific"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Add version metadata
            result = func(*args, **kwargs)
            
            if isinstance(result, dict):
                result['_api_version'] = version
            
            return result
        
        # Store version metadata
        wrapper._api_version = version
        return wrapper
    return decorator


# Version compatibility checker
class VersionCompatibility:
    """Check compatibility between API versions"""
    
    @staticmethod
    def is_compatible(source_version: str, target_version: str) -> bool:
        """Check if versions are compatible"""
        # Extract major version numbers
        source_major = int(source_version.replace('v', '').split('.')[0])
        target_major = int(target_version.replace('v', '').split('.')[0])
        
        # Same major version = compatible
        return source_major == target_major
    
    @staticmethod
    def get_breaking_changes(
        from_version: str,
        to_version: str,
        version_manager: APIVersionManager
    ) -> List[str]:
        """Get breaking changes between versions"""
        from_v = version_manager.get_version(from_version)
        to_v = version_manager.get_version(to_version)
        
        if not from_v or not to_v:
            return []
        
        # In real implementation, track breaking changes
        if not VersionCompatibility.is_compatible(from_version, to_version):
            return [
                f"Major version change from {from_version} to {to_version}",
                "Breaking changes may exist",
                "Review migration guide"
            ]
        
        return []


# Test code
if __name__ == "__main__":
    print("🔄 Testing API Versioning...")
    
    # Initialize version manager
    vm = APIVersionManager()
    
    # List versions
    print("\n📋 Available API versions:")
    for version in vm.list_versions():
        status_emoji = "✅" if version['status'] == 'active' else "⚠️" if version['status'] == 'deprecated' else "❌"
        print(f"  {status_emoji} {version['version']} - {version['status']}")
        print(f"     Released: {version['release_date']}")
        if version['changes']:
            print(f"     Changes: {len(version['changes'])} features")
    
    # Get latest version
    print(f"\n🆕 Latest version: {vm.get_latest_version()}")
    
    # Deprecate v1
    print("\n⚠️ Deprecating v1...")
    vm.deprecate_version(
        "v1",
        sunset_date=(datetime.now() + timedelta(days=180)).isoformat()
    )
    
    # Get deprecation warning
    warning = vm.get_deprecation_warning("v1")
    if warning:
        print(f"  Warning: {warning['warning']}")
        print(f"  Sunset date: {warning['sunset_date']}")
        print(f"  Migrate to: {warning['latest_version']}")
    
    # Test version router
    print("\n🔀 Testing version router...")
    router = APIVersionRouter(vm)
    
    # Define v1 handler
    def get_user_v1(user_id: str):
        return {"user_id": user_id, "name": "User", "version": "v1"}
    
    # Define v2 handler (enhanced)
    def get_user_v2(user_id: str):
        return {
            "user_id": user_id,
            "name": "User",
            "email": "user@example.com",
            "roles": ["user"],
            "version": "v2"
        }
    
    # Register endpoints
    router.register_endpoint("/users", "v1", get_user_v1)
    router.register_endpoint("/users", "v2", get_user_v2)
    
    # Route requests
    result_v1 = router.route_request("/users", "v1", user_id="123")
    result_v2 = router.route_request("/users", "v2", user_id="123")
    
    print(f"  V1 response: {result_v1}")
    print(f"  V2 response: {result_v2}")
    
    # Check compatibility
    print("\n🔍 Version compatibility:")
    print(f"  v1 → v2: {VersionCompatibility.is_compatible('v1', 'v2')}")
    print(f"  v2 → v3: {VersionCompatibility.is_compatible('v2', 'v3')}")
    
    print("\n✅ API Versioning test complete!")
