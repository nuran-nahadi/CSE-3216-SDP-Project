#!/usr/bin/env python3
"""
Test script for LIN Expense Management API endpoints
"""

import requests
import json
from datetime import datetime, timedelta
import uuid

# Configuration
BASE_URL = "http://localhost:8000"
USERNAME = "testuser"
EMAIL = "test@example.com"
PASSWORD = "testpassword123"

def test_expense_endpoints():
    """Test all expense-related endpoints"""
    
    # Step 1: Register and login to get token
    print("🔑 Step 1: Authentication")
    
    # Register user
    register_data = {
        "full_name": "Test User",
        "username": USERNAME,
        "email": EMAIL,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json=register_data)
        if response.status_code == 201:
            print("✅ User registered successfully")
        else:
            print("ℹ️ User might already exist, proceeding with login")
    except Exception as e:
        print(f"⚠️ Registration error: {e}")
    
    # Login to get token
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
            print("✅ Login successful, token obtained")
        else:
            print(f"❌ Login failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 2: Test expense creation
    print("\n💰 Step 2: Create Expenses")
    
    # Create sample expenses
    sample_expenses = [
        {
            "amount": 12.50,
            "currency": "USD",
            "category": "food",
            "subcategory": "coffee",
            "merchant": "Starbucks",
            "description": "Morning coffee",
            "date": datetime.now().isoformat(),
            "payment_method": "credit_card",
            "tags": ["morning", "caffeine"]
        },
        {
            "amount": 35.75,
            "currency": "USD",
            "category": "food",
            "subcategory": "dinner",
            "merchant": "Italian Restaurant",
            "description": "Dinner with friends",
            "date": (datetime.now() - timedelta(days=1)).isoformat(),
            "payment_method": "credit_card",
            "tags": ["dinner", "social"]
        },
        {
            "amount": 15.00,
            "currency": "USD",
            "category": "transport",
            "subcategory": "taxi",
            "merchant": "Uber",
            "description": "Ride to work",
            "date": (datetime.now() - timedelta(days=2)).isoformat(),
            "payment_method": "digital_wallet",
            "tags": ["commute"]
        }
    ]
    
    created_expense_ids = []
    
    for i, expense_data in enumerate(sample_expenses):
        try:
            response = requests.post(f"{BASE_URL}/expenses", json=expense_data, headers=headers)
            if response.status_code == 201:
                expense = response.json()["data"]
                created_expense_ids.append(expense["id"])
                print(f"✅ Created expense {i+1}: ${expense['amount']} for {expense['category']}")
            else:
                print(f"❌ Failed to create expense {i+1}: {response.text}")
        except Exception as e:
            print(f"❌ Error creating expense {i+1}: {e}")
    
    # Step 3: Test getting expenses
    print("\n📋 Step 3: Retrieve Expenses")
    
    try:
        response = requests.get(f"{BASE_URL}/expenses", headers=headers)
        if response.status_code == 200:
            expenses_data = response.json()
            expenses = expenses_data["data"]
            print(f"✅ Retrieved {len(expenses)} expenses")
            print(f"ℹ️ Total pages: {expenses_data['meta']['pages']}")
        else:
            print(f"❌ Failed to retrieve expenses: {response.text}")
    except Exception as e:
        print(f"❌ Error retrieving expenses: {e}")
    
    # Step 4: Test expense filtering
    print("\n🔍 Step 4: Filter Expenses")
    
    try:
        # Filter by category
        response = requests.get(f"{BASE_URL}/expenses?category=food", headers=headers)
        if response.status_code == 200:
            food_expenses = response.json()["data"]
            print(f"✅ Found {len(food_expenses)} food expenses")
        
        # Filter by amount range
        response = requests.get(f"{BASE_URL}/expenses?min_amount=20&max_amount=50", headers=headers)
        if response.status_code == 200:
            filtered_expenses = response.json()["data"]
            print(f"✅ Found {len(filtered_expenses)} expenses in $20-$50 range")
    except Exception as e:
        print(f"❌ Error filtering expenses: {e}")
    
    # Step 5: Test specific expense retrieval
    print("\n🎯 Step 5: Get Specific Expense")
    
    if created_expense_ids:
        try:
            expense_id = created_expense_ids[0]
            response = requests.get(f"{BASE_URL}/expenses/{expense_id}", headers=headers)
            if response.status_code == 200:
                expense = response.json()["data"]
                print(f"✅ Retrieved expense: ${expense['amount']} at {expense['merchant']}")
            else:
                print(f"❌ Failed to retrieve specific expense: {response.text}")
        except Exception as e:
            print(f"❌ Error retrieving specific expense: {e}")
    
    # Step 6: Test expense update
    print("\n✏️ Step 6: Update Expense")
    
    if created_expense_ids:
        try:
            expense_id = created_expense_ids[0]
            update_data = {
                "amount": 13.00,
                "description": "Large morning coffee (updated)"
            }
            response = requests.put(f"{BASE_URL}/expenses/{expense_id}", json=update_data, headers=headers)
            if response.status_code == 200:
                updated_expense = response.json()["data"]
                print(f"✅ Updated expense: ${updated_expense['amount']} - {updated_expense['description']}")
            else:
                print(f"❌ Failed to update expense: {response.text}")
        except Exception as e:
            print(f"❌ Error updating expense: {e}")
    
    # Step 7: Test natural language parsing
    print("\n🤖 Step 7: Parse Natural Language")
    
    test_phrases = [
        "I spent $25 on lunch at McDonald's",
        "Paid 50 dollars for gas yesterday",
        "Coffee cost me 4.50 this morning"
    ]
    
    for phrase in test_phrases:
        try:
            parse_data = {"text": phrase}
            response = requests.post(f"{BASE_URL}/expenses/parse", json=parse_data, headers=headers)
            if response.status_code == 200:
                parsed = response.json()["data"]
                print(f"✅ Parsed: '{phrase}' → ${parsed['amount']} ({parsed['category']})")
            else:
                print(f"❌ Failed to parse: '{phrase}'")
        except Exception as e:
            print(f"❌ Error parsing: '{phrase}' - {e}")
    
    # Step 8: Test expense summary
    print("\n📊 Step 8: Get Expense Summary")
    
    try:
        response = requests.get(f"{BASE_URL}/expenses/summary", headers=headers)
        if response.status_code == 200:
            summary = response.json()["data"]
            print(f"✅ Total expenses: ${summary['total_amount']:.2f}")
            print(f"✅ Average expense: ${summary['average_amount']:.2f}")
            print(f"✅ Total count: {summary['total_count']}")
            print("✅ Categories:")
            for cat in summary['categories']:
                print(f"   - {cat['category']}: ${cat['total_amount']:.2f} ({cat['percentage']:.1f}%)")
        else:
            print(f"❌ Failed to get summary: {response.text}")
    except Exception as e:
        print(f"❌ Error getting summary: {e}")
    
    # Step 9: Test categories summary
    print("\n📈 Step 9: Get Categories")
    
    try:
        response = requests.get(f"{BASE_URL}/expenses/categories", headers=headers)
        if response.status_code == 200:
            categories = response.json()["data"]
            print(f"✅ Found {len(categories)} expense categories")
            for cat in categories:
                print(f"   - {cat['category']}: ${cat['total_amount']:.2f} ({cat['count']} expenses)")
        else:
            print(f"❌ Failed to get categories: {response.text}")
    except Exception as e:
        print(f"❌ Error getting categories: {e}")
    
    # Step 10: Test monthly expenses
    print("\n📅 Step 10: Get Monthly Expenses")
    
    try:
        current_year = datetime.now().year
        current_month = datetime.now().month
        response = requests.get(f"{BASE_URL}/expenses/monthly/{current_year}/{current_month}", headers=headers)
        if response.status_code == 200:
            monthly = response.json()["data"]
            print(f"✅ {current_month}/{current_year}: ${monthly['total_amount']:.2f} ({monthly['count']} expenses)")
        else:
            print(f"❌ Failed to get monthly expenses: {response.text}")
    except Exception as e:
        print(f"❌ Error getting monthly expenses: {e}")
    
    # Step 11: Test recurring expenses
    print("\n🔄 Step 11: Get Recurring Expenses")
    
    try:
        response = requests.get(f"{BASE_URL}/expenses/recurring", headers=headers)
        if response.status_code == 200:
            recurring = response.json()["data"]
            print(f"✅ Found {len(recurring)} recurring expenses")
        else:
            print(f"❌ Failed to get recurring expenses: {response.text}")
    except Exception as e:
        print(f"❌ Error getting recurring expenses: {e}")
    
    # Step 12: Test bulk import
    print("\n📥 Step 12: Bulk Import")
    
    bulk_expenses = [
        {
            "amount": 8.50,
            "currency": "USD",
            "category": "food",
            "description": "Breakfast sandwich",
            "date": datetime.now().isoformat()
        },
        {
            "amount": 22.00,
            "currency": "USD",
            "category": "entertainment",
            "description": "Movie ticket",
            "date": datetime.now().isoformat()
        }
    ]
    
    try:
        bulk_data = {"expenses": bulk_expenses}
        response = requests.post(f"{BASE_URL}/expenses/bulk", json=bulk_data, headers=headers)
        if response.status_code == 201:
            imported = response.json()["data"]
            print(f"✅ Bulk imported {len(imported)} expenses")
        else:
            print(f"❌ Failed to bulk import: {response.text}")
    except Exception as e:
        print(f"❌ Error bulk importing: {e}")
    
    # Step 13: Test export
    print("\n📤 Step 13: Export Expenses")
    
    try:
        # Export as JSON
        response = requests.get(f"{BASE_URL}/expenses/export?format=json", headers=headers)
        if response.status_code == 200:
            exported = response.json()["data"]
            print(f"✅ Exported {len(exported)} expenses as JSON")
        
        # Export as CSV
        response = requests.get(f"{BASE_URL}/expenses/export?format=csv", headers=headers)
        if response.status_code == 200:
            csv_data = response.json()["data"]
            lines = csv_data.split('\n')
            print(f"✅ Exported CSV with {len(lines)-1} data rows")
    except Exception as e:
        print(f"❌ Error exporting: {e}")
    
    # Step 14: Test expense deletion
    print("\n🗑️ Step 14: Delete Expense")
    
    if created_expense_ids and len(created_expense_ids) > 1:
        try:
            expense_id = created_expense_ids[-1]  # Delete the last one
            response = requests.delete(f"{BASE_URL}/expenses/{expense_id}", headers=headers)
            if response.status_code == 200:
                deleted_expense = response.json()["data"]
                print(f"✅ Deleted expense: ${deleted_expense['amount']} at {deleted_expense['merchant']}")
            else:
                print(f"❌ Failed to delete expense: {response.text}")
        except Exception as e:
            print(f"❌ Error deleting expense: {e}")
    
    print("\n🎉 Expense API testing completed!")
    print("📊 Summary:")
    print("   - Created multiple expenses")
    print("   - Retrieved and filtered expenses")
    print("   - Updated expense details")
    print("   - Parsed natural language")
    print("   - Generated summaries and reports")
    print("   - Tested bulk operations")
    print("   - Exported data")
    print("   - Cleaned up test data")


if __name__ == "__main__":
    print("🧪 LIN Expense Management API Test Suite")
    print("=" * 50)
    test_expense_endpoints()
