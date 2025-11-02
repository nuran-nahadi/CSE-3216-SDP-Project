"""
Test file for Events API endpoints
Run this script to test all events functionality
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any


class EventAPITester:
    def __init__(self, base_url: str = "http://localhost:8000", access_token: str = None):
        self.base_url = base_url
        self.access_token = access_token
        self.headers = {}
        if access_token:
            self.headers["Authorization"] = f"Bearer {access_token}"
    
    def set_token(self, token: str):
        """Set the authorization token"""
        self.access_token = token
        self.headers["Authorization"] = f"Bearer {token}"
    
    def test_create_event(self) -> Dict[str, Any]:
        """Test creating a new event"""
        print("\n--- Testing Create Event ---")
        
        event_data = {
            "title": "Test Meeting",
            "description": "This is a test meeting created by API test",
            "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
            "location": "Conference Room A",
            "tags": ["work", "meeting"],
            "is_all_day": False,
            "reminder_minutes": 15,
            "color": "#FF5733"
        }
        
        response = requests.post(
            f"{self.base_url}/events/",
            json=event_data,
            headers=self.headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
        
        if response.status_code == 201:
            return response.json()["data"]
        return None
    
    def test_get_events(self) -> Dict[str, Any]:
        """Test getting list of events"""
        print("\n--- Testing Get Events ---")
        
        response = requests.get(
            f"{self.base_url}/events/",
            headers=self.headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
        
        return response.json()
    
    def test_get_event_by_id(self, event_id: str) -> Dict[str, Any]:
        """Test getting a specific event by ID"""
        print(f"\n--- Testing Get Event by ID: {event_id} ---")
        
        response = requests.get(
            f"{self.base_url}/events/{event_id}",
            headers=self.headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
        
        return response.json()
    
    def test_update_event(self, event_id: str) -> Dict[str, Any]:
        """Test updating an event"""
        print(f"\n--- Testing Update Event: {event_id} ---")
        
        update_data = {
            "title": "Updated Test Meeting",
            "description": "This meeting has been updated",
            "location": "Conference Room B",
            "tags": ["work", "meeting", "updated"]
        }
        
        response = requests.put(
            f"{self.base_url}/events/{event_id}",
            json=update_data,
            headers=self.headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
        
        return response.json()
    
    def test_get_calendar_view(self) -> Dict[str, Any]:
        """Test getting calendar view"""
        print("\n--- Testing Get Calendar View ---")
        
        now = datetime.now()
        response = requests.get(
            f"{self.base_url}/events/calendar/{now.year}/{now.month}",
            headers=self.headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
        
        return response.json()
    
    def test_get_upcoming_events(self) -> Dict[str, Any]:
        """Test getting upcoming events"""
        print("\n--- Testing Get Upcoming Events ---")
        
        response = requests.get(
            f"{self.base_url}/events/upcoming",
            headers=self.headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
        
        return response.json()
    
    def test_parse_natural_language(self) -> Dict[str, Any]:
        """Test parsing natural language"""
        print("\n--- Testing Parse Natural Language ---")
        
        parse_data = {
            "text": "Lunch with Sarah tomorrow at noon"
        }
        
        response = requests.post(
            f"{self.base_url}/events/parse",
            json=parse_data,
            headers=self.headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
        
        return response.json()
    
    def test_delete_event(self, event_id: str) -> Dict[str, Any]:
        """Test deleting an event"""
        print(f"\n--- Testing Delete Event: {event_id} ---")
        
        response = requests.delete(
            f"{self.base_url}/events/{event_id}",
            headers=self.headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
        
        return response.json()
    
    def run_all_tests(self):
        """Run all event tests"""
        print("Starting Events API Tests...")
        
        # Test creating an event
        created_event = self.test_create_event()
        if not created_event:
            print("Failed to create event. Stopping tests.")
            return
        
        event_id = created_event["id"]
        
        # Test getting all events
        self.test_get_events()
        
        # Test getting specific event
        self.test_get_event_by_id(event_id)
        
        # Test updating event
        self.test_update_event(event_id)
        
        # Test calendar view
        self.test_get_calendar_view()
        
        # Test upcoming events
        self.test_get_upcoming_events()
        
        # Test natural language parsing
        self.test_parse_natural_language()
        
        # Test deleting event
        self.test_delete_event(event_id)
        
        print("\n--- All tests completed! ---")


def test_with_authentication():
    """Test events API with authentication"""
    # First, you need to get an access token by logging in
    print("To run tests with authentication:")
    print("1. Start the server: python run.py")
    print("2. Get an access token by logging in")
    print("3. Replace 'YOUR_ACCESS_TOKEN' with the actual token")
    
    access_token = "YOUR_ACCESS_TOKEN"  # Replace with actual token
    
    tester = EventAPITester(access_token=access_token)
    tester.run_all_tests()


def test_without_authentication():
    """Test events API without authentication (if auth is disabled)"""
    tester = EventAPITester()
    tester.run_all_tests()


if __name__ == "__main__":
    print("Events API Test Suite")
    print("Choose test mode:")
    print("1. With authentication (default)")
    print("2. Without authentication (if auth is disabled)")
    
    choice = input("Enter choice (1 or 2): ").strip() or "1"
    
    if choice == "2":
        test_without_authentication()
    else:
        test_with_authentication()
