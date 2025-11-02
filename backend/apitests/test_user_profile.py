"""
Test script for User Profile endpoints
Run this after starting the server to test the endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)


def test_user_profile_endpoints(access_token):
    """Test user profile endpoints with authentication"""
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Test GET /users/me
    print("Testing GET /users/me")
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
    print("-" * 50)
    
    # Test PUT /users/me
    print("Testing PUT /users/me")
    update_data = {
        "first_name": "Updated",
        "last_name": "Name",
        "timezone": "America/New_York"
    }
    response = requests.put(f"{BASE_URL}/users/me", headers=headers, json=update_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
    print("-" * 50)
    
    # Test GET /users/me/preferences
    print("Testing GET /users/me/preferences")
    response = requests.get(f"{BASE_URL}/users/me/preferences", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
    print("-" * 50)
    
    # Test PUT /users/me/preferences
    print("Testing PUT /users/me/preferences")
    preferences_data = {
        "theme": "dark",
        "default_expense_currency": "EUR",
        "time_format": "24h",
        "ai_insights_enabled": True,
        "notification_settings": {
            "email": True,
            "push": False,
            "in_app": True
        }
    }
    response = requests.put(f"{BASE_URL}/users/me/preferences", headers=headers, json=preferences_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
    print("-" * 50)


def main():
    """Main test function"""
    print("Testing User Profile Endpoints")
    print("=" * 50)
    
    # Test health check first
    test_health_check()
    
    # Note: You'll need to get an access token by logging in first
    print("To test authenticated endpoints:")
    print("1. Start the server: uvicorn app.main:app --reload")
    print("2. Login via POST /auth/login to get access token")
    print("3. Pass the access token to test_user_profile_endpoints()")
    print("\nExample:")
    print("access_token = 'your_jwt_token_here'")
    print("test_user_profile_endpoints(access_token)")


if __name__ == "__main__":
    main()
