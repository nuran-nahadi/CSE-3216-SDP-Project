"""
Test file for Tasks API endpoints
Run this script to test all tasks functionality
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any


class TaskAPITester:
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
    
    def test_create_task(self) -> Dict[str, Any]:
        """Test creating a new task"""
        print("\n--- Testing Create Task ---")
        
        task_data = {
            "title": "Complete API Documentation",
            "description": "Write comprehensive API documentation for the new endpoints",
            "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
            "priority": "high",
            "status": "pending",
            "estimated_duration": 120,
            "tags": ["documentation", "api", "work"]
        }
        
        response = requests.post(
            f"{self.base_url}/tasks/",
            json=task_data,
            headers=self.headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
        
        if response.status_code == 201:
            print("✅ Task creation successful!")
            return response.json()["data"]
        else:
            print("❌ Task creation failed!")
            return None
    
    def test_get_tasks(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Test getting tasks with optional filters"""
        print("\n--- Testing Get Tasks ---")
        
        params = {}
        if filters:
            params.update(filters)
        
        response = requests.get(
            f"{self.base_url}/tasks/",
            params=params,
            headers=self.headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
        
        if response.status_code == 200:
            print("✅ Get tasks successful!")
            return response.json()
        else:
            print("❌ Get tasks failed!")
            return None
    
    def test_get_task_by_id(self, task_id: str) -> Dict[str, Any]:
        """Test getting a specific task by ID"""
        print(f"\n--- Testing Get Task by ID: {task_id} ---")
        
        response = requests.get(
            f"{self.base_url}/tasks/{task_id}",
            headers=self.headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
        
        if response.status_code == 200:
            print("✅ Get task by ID successful!")
            return response.json()["data"]
        else:
            print("❌ Get task by ID failed!")
            return None
    
    def test_update_task(self, task_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test updating a task"""
        print(f"\n--- Testing Update Task: {task_id} ---")
        
        response = requests.put(
            f"{self.base_url}/tasks/{task_id}",
            json=update_data,
            headers=self.headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
        
        if response.status_code == 200:
            print("✅ Task update successful!")
            return response.json()["data"]
        else:
            print("❌ Task update failed!")
            return None
    
    def test_complete_task(self, task_id: str, actual_duration: int = None) -> Dict[str, Any]:
        """Test marking a task as completed"""
        print(f"\n--- Testing Complete Task: {task_id} ---")
        
        complete_data = {}
        if actual_duration:
            complete_data["actual_duration"] = actual_duration
        
        response = requests.patch(
            f"{self.base_url}/tasks/{task_id}/complete",
            json=complete_data,
            headers=self.headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
        
        if response.status_code == 200:
            print("✅ Task completion successful!")
            return response.json()["data"]
        else:
            print("❌ Task completion failed!")
            return None
    
    def test_get_today_tasks(self) -> Dict[str, Any]:
        """Test getting today's tasks"""
        print("\n--- Testing Get Today's Tasks ---")
        
        response = requests.get(
            f"{self.base_url}/tasks/today",
            headers=self.headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
        
        if response.status_code == 200:
            print("✅ Get today's tasks successful!")
            return response.json()
        else:
            print("❌ Get today's tasks failed!")
            return None
    
    def test_get_overdue_tasks(self) -> Dict[str, Any]:
        """Test getting overdue tasks"""
        print("\n--- Testing Get Overdue Tasks ---")
        
        response = requests.get(
            f"{self.base_url}/tasks/overdue",
            headers=self.headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
        
        if response.status_code == 200:
            print("✅ Get overdue tasks successful!")
            return response.json()
        else:
            print("❌ Get overdue tasks failed!")
            return None
    
    def test_parse_task_text(self, text: str) -> Dict[str, Any]:
        """Test parsing natural language text into task data"""
        print(f"\n--- Testing Parse Task Text: {text} ---")
        
        parse_data = {"text": text}
        
        response = requests.post(
            f"{self.base_url}/tasks/parse",
            json=parse_data,
            headers=self.headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
        
        if response.status_code == 200:
            print("✅ Parse task text successful!")
            return response.json()["data"]
        else:
            print("❌ Parse task text failed!")
            return None
    
    def test_delete_task(self, task_id: str) -> bool:
        """Test deleting a task"""
        print(f"\n--- Testing Delete Task: {task_id} ---")
        
        response = requests.delete(
            f"{self.base_url}/tasks/{task_id}",
            headers=self.headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
        
        if response.status_code == 200:
            print("✅ Task deletion successful!")
            return True
        else:
            print("❌ Task deletion failed!")
            return False
    
    def run_comprehensive_test(self):
        """Run a comprehensive test of all task endpoints"""
        print("🚀 Starting comprehensive Task API tests...")
        
        # 1. Create a test task
        task = self.test_create_task()
        if not task:
            print("❌ Cannot continue tests - task creation failed")
            return
        
        task_id = task["id"]
        
        # 2. Get all tasks
        self.test_get_tasks()
        
        # 3. Get tasks with filters
        self.test_get_tasks({"priority": "high", "status": "pending"})
        
        # 4. Get specific task by ID
        self.test_get_task_by_id(task_id)
        
        # 5. Update the task
        update_data = {
            "description": "Updated description with more details",
            "priority": "medium",
            "tags": ["documentation", "api", "work", "updated"]
        }
        self.test_update_task(task_id, update_data)
        
        # 6. Test natural language parsing
        self.test_parse_task_text("Remind me to call mom tomorrow at 3 PM #family")
        self.test_parse_task_text("High priority task to review budget by next week")
        
        # 7. Get today's tasks
        self.test_get_today_tasks()
        
        # 8. Get overdue tasks
        self.test_get_overdue_tasks()
        
        # 9. Complete the task
        self.test_complete_task(task_id, actual_duration=90)
        
        # 10. Verify task is completed
        completed_task = self.test_get_task_by_id(task_id)
        if completed_task and completed_task["status"] == "completed":
            print("✅ Task completion verification successful!")
        
        # 11. Clean up - delete the task
        self.test_delete_task(task_id)
        
        print("\n🎉 Comprehensive Task API tests completed!")


def authenticate_and_test():
    """Authenticate user and run tests"""
    tester = TaskAPITester()
    
    # You can either set a token directly or login first
    # For testing, you might want to use a valid token
    
    print("Please provide authentication:")
    print("1. Enter a valid access token")
    print("2. Or login with credentials (you'll need to implement login)")
    
    token = input("Enter access token (or press Enter to skip): ").strip()
    
    if token:
        tester.set_token(token)
        tester.run_comprehensive_test()
    else:
        print("No token provided. Please authenticate first.")
        print("You can get a token by:")
        print("1. Login via /auth/login endpoint")
        print("2. Or use an existing valid token")


if __name__ == "__main__":
    authenticate_and_test()
