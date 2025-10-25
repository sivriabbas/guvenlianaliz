"""
Phase 8.F Test Suite - Advanced Security Features
OAuth2, JWT, RBAC, API Versioning tests
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8003"

# Color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(name, passed, details=""):
    """Print test result"""
    symbol = "✅" if passed else "❌"
    color = Colors.GREEN if passed else Colors.RED
    print(f"{color}{symbol} {name}{Colors.RESET}")
    if details:
        print(f"   {details}")

# Test 1: System Status Check
def test_system_status():
    """Test if Phase 8.F is listed in system status"""
    try:
        response = requests.get(f"{BASE_URL}/api/system-status")
        data = response.json()
        
        # Navigate to correct path in response
        status = data.get('status', {})
        phase8 = status.get('phase8', {})
        has_security = 'F_security' in phase8
        has_features = has_security and phase8['F_security']['available']
        
        details = ""
        if has_security:
            features = phase8['F_security']['features']
            endpoints = phase8['F_security']['endpoints']
            details = f"Features: {len(features)}, Endpoints: {len(endpoints)}"
        
        print_test("System Status - Phase 8.F", has_security and has_features, details)
        return has_security and has_features
    except Exception as e:
        print_test("System Status - Phase 8.F", False, str(e))
        return False

# Test 2: OAuth2 Client Registration
def test_oauth2_client_registration():
    """Test OAuth2 client registration"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/v2/auth/register-client",
            params={
                "client_name": "Test Client",
                "redirect_uri": "http://localhost:8000/callback"
            }
        )
        data = response.json()
        
        has_client_id = 'client_id' in data
        has_client_secret = 'client_secret' in data
        success = has_client_id and has_client_secret
        
        details = ""
        if success:
            details = f"Client ID: {data['client_id'][:20]}..., Secret: {data['client_secret'][:20]}..."
            # Store for later tests
            global CLIENT_ID, CLIENT_SECRET
            CLIENT_ID = data['client_id']
            CLIENT_SECRET = data['client_secret']
        else:
            details = data.get('error', 'Unknown error')
        
        print_test("OAuth2 Client Registration", success, details)
        return success
    except Exception as e:
        print_test("OAuth2 Client Registration", False, str(e))
        return False

# Test 3: OAuth2 Authorization Code
def test_oauth2_authorization():
    """Test OAuth2 authorization code creation"""
    try:
        if not CLIENT_ID:
            print_test("OAuth2 Authorization", False, "No client ID available")
            return False
        
        response = requests.post(
            f"{BASE_URL}/api/v2/auth/authorize",
            params={
                "client_id": CLIENT_ID,
                "user_id": "test_user_123",
                "redirect_uri": "http://localhost:8000/callback",
                "scope": "read write"
            }
        )
        data = response.json()
        
        has_code = 'code' in data
        has_expires = 'expires_in' in data
        success = has_code and has_expires
        
        details = ""
        if success:
            details = f"Code: {data['code'][:20]}..., Expires: {data['expires_in']}s"
            # Store for token exchange
            global AUTH_CODE
            AUTH_CODE = data['code']
        else:
            details = data.get('error', 'Unknown error')
        
        print_test("OAuth2 Authorization Code", success, details)
        return success
    except Exception as e:
        print_test("OAuth2 Authorization Code", False, str(e))
        return False

# Test 4: OAuth2 Token Exchange
def test_oauth2_token_exchange():
    """Test OAuth2 token exchange"""
    try:
        if not AUTH_CODE or not CLIENT_ID or not CLIENT_SECRET:
            print_test("OAuth2 Token Exchange", False, "Missing auth code or credentials")
            return False
        
        response = requests.post(
            f"{BASE_URL}/api/v2/auth/token",
            params={
                "grant_type": "authorization_code",
                "code": AUTH_CODE,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": "http://localhost:8000/callback"
            }
        )
        data = response.json()
        
        has_access = 'access_token' in data
        has_refresh = 'refresh_token' in data
        has_jwt_access = 'jwt_access_token' in data
        has_jwt_refresh = 'jwt_refresh_token' in data
        success = has_access and has_refresh and has_jwt_access and has_jwt_refresh
        
        details = ""
        if success:
            details = f"OAuth2 + JWT tokens received, Type: {data.get('token_type')}"
            # Store tokens
            global ACCESS_TOKEN, REFRESH_TOKEN, JWT_ACCESS, JWT_REFRESH
            ACCESS_TOKEN = data['access_token']
            REFRESH_TOKEN = data['refresh_token']
            JWT_ACCESS = data['jwt_access_token']
            JWT_REFRESH = data['jwt_refresh_token']
        else:
            details = data.get('error', 'Token exchange failed')
        
        print_test("OAuth2 Token Exchange", success, details)
        return success
    except Exception as e:
        print_test("OAuth2 Token Exchange", False, str(e))
        return False

# Test 5: JWT Token Refresh
def test_jwt_refresh():
    """Test JWT token refresh"""
    try:
        if not JWT_REFRESH:
            print_test("JWT Token Refresh", False, "No refresh token available")
            return False
        
        response = requests.post(
            f"{BASE_URL}/api/v2/auth/refresh",
            params={"refresh_token": JWT_REFRESH}
        )
        data = response.json()
        
        has_access = 'access_token' in data
        has_type = 'token_type' in data
        success = has_access and has_type
        
        details = ""
        if success:
            details = f"New access token: {data['access_token'][:20]}..., Type: {data['token_type']}"
        else:
            details = data.get('error', 'Refresh failed')
        
        print_test("JWT Token Refresh", success, details)
        return success
    except Exception as e:
        print_test("JWT Token Refresh", False, str(e))
        return False

# Test 6: RBAC - List Roles
def test_rbac_roles():
    """Test RBAC role listing"""
    try:
        response = requests.get(f"{BASE_URL}/api/v2/rbac/roles")
        data = response.json()
        
        has_roles = 'roles' in data
        has_total = 'total' in data
        success = has_roles and has_total and data['total'] > 0
        
        details = ""
        if success:
            role_names = [r['role_name'] for r in data['roles']]
            details = f"Found {data['total']} roles: {', '.join(role_names)}"
        else:
            details = data.get('error', 'No roles found')
        
        print_test("RBAC - List Roles", success, details)
        return success
    except Exception as e:
        print_test("RBAC - List Roles", False, str(e))
        return False

# Test 7: RBAC - List Permissions
def test_rbac_permissions():
    """Test RBAC permission listing"""
    try:
        response = requests.get(f"{BASE_URL}/api/v2/rbac/permissions")
        data = response.json()
        
        has_permissions = 'permissions' in data
        has_total = 'total' in data
        has_by_resource = 'by_resource' in data
        success = has_permissions and has_total and data['total'] > 0
        
        details = ""
        if success:
            resources = list(data.get('by_resource', {}).keys())
            details = f"Found {data['total']} permissions across {len(resources)} resources"
        else:
            details = data.get('error', 'No permissions found')
        
        print_test("RBAC - List Permissions", success, details)
        return success
    except Exception as e:
        print_test("RBAC - List Permissions", False, str(e))
        return False

# Test 8: RBAC - Assign Role
def test_rbac_assign_role():
    """Test RBAC role assignment"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/v2/rbac/assign-role",
            params={
                "user_id": "test_user_123",
                "role_name": "developer"
            }
        )
        data = response.json()
        
        success = data.get('success', False)
        
        details = ""
        if success:
            details = f"Role '{data.get('role')}' assigned to {data.get('user_id')}"
        else:
            details = data.get('error', 'Assignment failed')
        
        print_test("RBAC - Assign Role", success, details)
        return success
    except Exception as e:
        print_test("RBAC - Assign Role", False, str(e))
        return False

# Test 9: RBAC - Get User Roles
def test_rbac_user_roles():
    """Test getting user roles and permissions"""
    try:
        response = requests.get(f"{BASE_URL}/api/v2/rbac/user/test_user_123/roles")
        data = response.json()
        
        has_roles = 'roles' in data
        has_permissions = 'permissions' in data
        has_user = data.get('user_id') == 'test_user_123'
        success = has_roles and has_permissions and has_user
        
        details = ""
        if success:
            roles_count = data.get('total_roles', 0)
            perms_count = data.get('total_permissions', 0)
            details = f"User has {roles_count} roles and {perms_count} permissions"
        else:
            details = data.get('error', 'User roles not found')
        
        print_test("RBAC - Get User Roles", success, details)
        return success
    except Exception as e:
        print_test("RBAC - Get User Roles", False, str(e))
        return False

# Test 10: API Versions
def test_api_versions():
    """Test API version listing"""
    try:
        response = requests.get(f"{BASE_URL}/api/v2/versions")
        data = response.json()
        
        has_versions = 'versions' in data
        has_latest = 'latest' in data
        has_default = 'default' in data
        success = has_versions and has_latest and has_default
        
        details = ""
        if success:
            version_numbers = [v['version'] for v in data['versions']]
            details = f"Available: {', '.join(version_numbers)}, Latest: {data['latest']}, Default: {data['default']}"
        else:
            details = data.get('error', 'Versions not found')
        
        print_test("API Versions", success, details)
        return success
    except Exception as e:
        print_test("API Versions", False, str(e))
        return False

# Test 11: Token Revocation
def test_token_revocation():
    """Test token revocation"""
    try:
        if not ACCESS_TOKEN:
            print_test("Token Revocation", False, "No access token available")
            return False
        
        response = requests.post(
            f"{BASE_URL}/api/v2/auth/revoke",
            params={
                "token": ACCESS_TOKEN,
                "token_type": "access_token"
            }
        )
        data = response.json()
        
        success = data.get('success', False)
        
        details = ""
        if success:
            details = f"Token revoked: {data.get('message')}"
        else:
            details = data.get('error', 'Revocation failed')
        
        print_test("Token Revocation", success, details)
        return success
    except Exception as e:
        print_test("Token Revocation", False, str(e))
        return False

# Global variables for test data
CLIENT_ID = None
CLIENT_SECRET = None
AUTH_CODE = None
ACCESS_TOKEN = None
REFRESH_TOKEN = None
JWT_ACCESS = None
JWT_REFRESH = None

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔐 PHASE 8.F - ADVANCED SECURITY FEATURES TEST SUITE")
    print("="*80 + "\n")
    
    print(f"{Colors.BLUE}Testing server: {BASE_URL}{Colors.RESET}\n")
    
    tests = [
        ("System Status", test_system_status),
        ("OAuth2 Client Registration", test_oauth2_client_registration),
        ("OAuth2 Authorization", test_oauth2_authorization),
        ("OAuth2 Token Exchange", test_oauth2_token_exchange),
        ("JWT Token Refresh", test_jwt_refresh),
        ("RBAC - List Roles", test_rbac_roles),
        ("RBAC - List Permissions", test_rbac_permissions),
        ("RBAC - Assign Role", test_rbac_assign_role),
        ("RBAC - Get User Roles", test_rbac_user_roles),
        ("API Versions", test_api_versions),
        ("Token Revocation", test_token_revocation),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_test(name, False, f"Exception: {e}")
            failed += 1
        
        # Small delay between tests
        time.sleep(0.2)
        print()
    
    # Summary
    print("="*80)
    total = passed + failed
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    if pass_rate == 100:
        color = Colors.GREEN
    elif pass_rate >= 70:
        color = Colors.YELLOW
    else:
        color = Colors.RED
    
    print(f"{color}SUMMARY: {passed}/{total} tests passed ({pass_rate:.1f}%){Colors.RESET}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print("="*80 + "\n")
    
    if passed == total:
        print(f"{Colors.GREEN}🎉 ALL TESTS PASSED! Phase 8.F is working perfectly!{Colors.RESET}\n")
    elif pass_rate >= 70:
        print(f"{Colors.YELLOW}⚠️ Most tests passed, but some features need attention.{Colors.RESET}\n")
    else:
        print(f"{Colors.RED}❌ Multiple failures detected. Please check the implementation.{Colors.RESET}\n")
