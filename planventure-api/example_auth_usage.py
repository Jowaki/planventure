"""
Example usage of the Authentication API.

This script demonstrates how to use the auth endpoints.
"""
import requests
import json

BASE_URL = "http://localhost:5000/auth"


def print_response(response, title=""):
    """Pretty print response"""
    if title:
        print(f"\n{'='*60}")
        print(f"{title}")
        print('='*60)
    
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))


def example_validate_email():
    """Example: Validate email"""
    print("\n>>> Validating email...")
    
    # Valid and available email
    response = requests.post(
        f"{BASE_URL}/validate-email",
        json={"email": "newuser@example.com"}
    )
    print_response(response, "Validate Email - Valid & Available")
    
    # Invalid format
    response = requests.post(
        f"{BASE_URL}/validate-email",
        json={"email": "invalid-email"}
    )
    print_response(response, "Validate Email - Invalid Format")


def example_password_strength():
    """Example: Check password strength"""
    print("\n>>> Checking password strength...")
    
    # Strong password
    response = requests.post(
        f"{BASE_URL}/password-strength",
        json={"password": "SecurePass123!"}
    )
    print_response(response, "Password Strength - Strong")
    
    # Weak password
    response = requests.post(
        f"{BASE_URL}/password-strength",
        json={"password": "weak"}
    )
    print_response(response, "Password Strength - Weak")


def example_registration():
    """Example: Register new user"""
    print("\n>>> Registering new user...")
    
    response = requests.post(
        f"{BASE_URL}/register",
        json={
            "email": "testuser@example.com",
            "password": "SecurePass123!"
        }
    )
    print_response(response, "User Registration")
    
    if response.status_code == 201:
        tokens = response.json()['auth']
        return tokens
    return None


def example_login(email="testuser@example.com", password="SecurePass123!"):
    """Example: Login user"""
    print("\n>>> Logging in user...")
    
    response = requests.post(
        f"{BASE_URL}/login",
        json={
            "email": email,
            "password": password
        }
    )
    print_response(response, "User Login")
    
    if response.status_code == 200:
        tokens = response.json()['auth']
        return tokens
    return None


def example_get_current_user(access_token):
    """Example: Get current user info"""
    print("\n>>> Getting current user info...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/me",
        headers=headers
    )
    print_response(response, "Get Current User")


def example_refresh_token(refresh_token):
    """Example: Refresh access token"""
    print("\n>>> Refreshing access token...")
    
    response = requests.post(
        f"{BASE_URL}/refresh",
        json={"refresh_token": refresh_token}
    )
    print_response(response, "Refresh Access Token")
    
    if response.status_code == 200:
        new_token = response.json()['auth']['access_token']
        return new_token
    return None


def example_invalid_credentials():
    """Example: Login with invalid credentials"""
    print("\n>>> Attempting login with invalid credentials...")
    
    response = requests.post(
        f"{BASE_URL}/login",
        json={
            "email": "nonexistent@example.com",
            "password": "WrongPassword123!"
        }
    )
    print_response(response, "Invalid Credentials Error")


def example_weak_password():
    """Example: Register with weak password"""
    print("\n>>> Attempting registration with weak password...")
    
    response = requests.post(
        f"{BASE_URL}/register",
        json={
            "email": "another@example.com",
            "password": "weak"
        }
    )
    print_response(response, "Weak Password Error")


def example_duplicate_email():
    """Example: Register with already used email"""
    print("\n>>> Attempting registration with duplicate email...")
    
    # First register
    requests.post(
        f"{BASE_URL}/register",
        json={
            "email": "duplicate@example.com",
            "password": "SecurePass123!"
        }
    )
    
    # Try to register again with same email
    response = requests.post(
        f"{BASE_URL}/register",
        json={
            "email": "duplicate@example.com",
            "password": "AnotherPass456!"
        }
    )
    print_response(response, "Duplicate Email Error")


if __name__ == "__main__":
    print("PlanVenture Authentication API Examples")
    print("========================================")
    
    # Run examples
    example_validate_email()
    example_password_strength()
    
    # Registration and login flow
    tokens = example_registration()
    
    if not tokens:
        # Try login if registration failed (e.g., user already exists)
        tokens = example_login()
    
    if tokens:
        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']
        
        # Use access token
        example_get_current_user(access_token)
        
        # Refresh token
        new_token = example_refresh_token(refresh_token)
    
    # Error examples
    example_invalid_credentials()
    example_weak_password()
    example_duplicate_email()
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60)
