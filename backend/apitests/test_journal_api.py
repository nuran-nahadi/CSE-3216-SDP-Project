"""
Journal API Test Script
Tests all journal endpoints with sample data
"""

import requests
import json
from datetime import datetime, timedelta


# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "journal_test_user",
    "email": "journal@test.com",
    "password": "test123456",
    "first_name": "Journal",
    "last_name": "Tester"
}


def get_auth_headers():
    """Get authentication headers for API requests"""
    # Login and get token
    login_response = requests.post(f"{BASE_URL}/auth/login", data={
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    })
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    else:
        print("❌ Failed to authenticate")
        return None


def test_journal_endpoints():
    """Test all journal endpoints"""
    
    print("🧪 Testing Journal API Endpoints")
    print("=" * 50)
    
    # Get authentication headers
    headers = get_auth_headers()
    if not headers:
        return
    
    # Test data
    journal_entries = [
        {
            "title": "Morning Reflections",
            "content": "Had a great morning workout today. Feeling energized and ready to tackle the day ahead. The weather is beautiful and I'm grateful for this opportunity to start fresh.",
            "mood": "happy",
            "weather": "Sunny, 72°F",
            "location": "Home"
        },
        {
            "title": "Project Update",
            "content": "Made significant progress on the LIN project today. Implemented the journal functionality and feeling accomplished. The team collaboration has been excellent.",
            "mood": "excited",
            "weather": "Partly cloudy",
            "location": "Office"
        },
        {
            "content": "Just a quick note about dinner with friends. Had an amazing time at the new restaurant downtown. Great food and even better company.",
            "mood": "grateful",
            "location": "Downtown Restaurant"
        }
    ]
    
    created_entries = []
    
    # Test 1: Create journal entries
    print("\n📝 Test 1: Creating journal entries")
    for i, entry_data in enumerate(journal_entries, 1):
        response = requests.post(
            f"{BASE_URL}/journal",
            headers=headers,
            json=entry_data
        )
        
        if response.status_code == 201:
            entry = response.json()["data"]
            created_entries.append(entry)
            print(f"✅ Created entry {i}: {entry['title'] or 'Untitled'}")
        else:
            print(f"❌ Failed to create entry {i}: {response.status_code}")
            print(f"   Response: {response.text}")
    
    if not created_entries:
        print("❌ No entries created, stopping tests")
        return
    
    # Test 2: Get all journal entries
    print("\n📋 Test 2: Retrieving all journal entries")
    response = requests.get(f"{BASE_URL}/journal", headers=headers)
    
    if response.status_code == 200:
        entries = response.json()["data"]
        meta = response.json()["meta"]
        print(f"✅ Retrieved {len(entries)} entries (Total: {meta['total']})")
    else:
        print(f"❌ Failed to retrieve entries: {response.status_code}")
    
    # Test 3: Get specific journal entry
    print("\n🔍 Test 3: Retrieving specific journal entry")
    if created_entries:
        entry_id = created_entries[0]["id"]
        response = requests.get(f"{BASE_URL}/journal/{entry_id}", headers=headers)
        
        if response.status_code == 200:
            entry = response.json()["data"]
            print(f"✅ Retrieved entry: {entry['title'] or 'Untitled'}")
        else:
            print(f"❌ Failed to retrieve entry: {response.status_code}")
    
    # Test 4: Update journal entry
    print("\n✏️ Test 4: Updating journal entry")
    if created_entries:
        entry_id = created_entries[0]["id"]
        update_data = {
            "title": "Updated Morning Reflections",
            "content": "Had a great morning workout today. Feeling even more energized after the update! The weather is still beautiful and I'm grateful for this opportunity to start fresh.",
            "mood": "very_happy"
        }
        
        response = requests.put(
            f"{BASE_URL}/journal/{entry_id}",
            headers=headers,
            json=update_data
        )
        
        if response.status_code == 200:
            entry = response.json()["data"]
            print(f"✅ Updated entry: {entry['title']}")
        else:
            print(f"❌ Failed to update entry: {response.status_code}")
    
    # Test 5: Search journal entries
    print("\n🔎 Test 5: Searching journal entries")
    search_params = {"search": "project"}
    response = requests.get(f"{BASE_URL}/journal", headers=headers, params=search_params)
    
    if response.status_code == 200:
        entries = response.json()["data"]
        print(f"✅ Found {len(entries)} entries matching 'project'")
    else:
        print(f"❌ Failed to search entries: {response.status_code}")
    
    # Test 6: Filter by mood
    print("\n😊 Test 6: Filtering by mood")
    mood_params = {"mood": "happy"}
    response = requests.get(f"{BASE_URL}/journal", headers=headers, params=mood_params)
    
    if response.status_code == 200:
        entries = response.json()["data"]
        print(f"✅ Found {len(entries)} entries with 'happy' mood")
    else:
        print(f"❌ Failed to filter by mood: {response.status_code}")
    
    # Test 7: Parse natural language
    print("\n🤖 Test 7: Parsing natural language")
    parse_data = {
        "text": "Today was an amazing day! I went for a run in the park and the weather was perfect. Feeling really grateful for my health and the beautiful surroundings."
    }
    
    response = requests.post(
        f"{BASE_URL}/journal/parse",
        headers=headers,
        json=parse_data
    )
    
    if response.status_code == 200:
        parsed = response.json()["data"]
        print(f"✅ Parsed text successfully")
        print(f"   Content: {parsed['content'][:50]}...")
    else:
        print(f"❌ Failed to parse text: {response.status_code}")
    
    # Test 8: Get journal statistics
    print("\n📊 Test 8: Getting journal statistics")
    response = requests.get(f"{BASE_URL}/journal/stats", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()["data"]
        print(f"✅ Retrieved statistics")
        print(f"   Total entries: {stats['total_entries']}")
        print(f"   Entries this month: {stats['entries_this_month']}")
        print(f"   Longest streak: {stats['longest_streak']}")
    else:
        print(f"❌ Failed to get statistics: {response.status_code}")
    
    # Test 9: Get mood trends
    print("\n📈 Test 9: Getting mood trends")
    response = requests.get(f"{BASE_URL}/journal/mood-trends", headers=headers, params={"days": 7})
    
    if response.status_code == 200:
        trends = response.json()["data"]
        print(f"✅ Retrieved mood trends for {trends['period_days']} days")
    else:
        print(f"❌ Failed to get mood trends: {response.status_code}")
    
    # Test 10: Trigger AI analysis
    print("\n🧠 Test 10: Triggering AI analysis")
    analysis_data = {
        "entry_ids": [entry["id"] for entry in created_entries[:2]]
    }
    
    response = requests.post(
        f"{BASE_URL}/journal/analyze",
        headers=headers,
        json=analysis_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Triggered analysis: {result['message']}")
    else:
        print(f"❌ Failed to trigger analysis: {response.status_code}")
    
    # Test 11: Delete journal entry
    print("\n🗑️ Test 11: Deleting journal entry")
    if created_entries:
        entry_id = created_entries[-1]["id"]
        response = requests.delete(f"{BASE_URL}/journal/{entry_id}", headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Deleted journal entry")
        else:
            print(f"❌ Failed to delete entry: {response.status_code}")
    
    print("\n🎉 Journal API tests completed!")


if __name__ == "__main__":
    test_journal_endpoints()
