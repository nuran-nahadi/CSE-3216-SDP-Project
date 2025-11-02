# Expense Management API Documentation

This document describes the Expense Management endpoints implemented for the LIN (Life Manager) application.

## Overview

The Expense endpoints allow authenticated users to track, manage, and analyze their financial expenses. These endpoints support natural language processing, receipt uploads, categorization, reporting, and bulk operations.

## Authentication

All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Data Models

### Expense Categories
- `food` - Food and dining expenses
- `transport` - Transportation costs
- `entertainment` - Entertainment and leisure
- `bills` - Utilities and recurring bills
- `shopping` - Shopping and retail
- `health` - Healthcare and medical
- `education` - Education and learning
- `travel` - Travel and vacation
- `other` - Miscellaneous expenses

### Payment Methods
- `cash` - Cash payments
- `credit_card` - Credit card
- `debit_card` - Debit card
- `bank_transfer` - Bank transfer
- `digital_wallet` - Digital wallets (PayPal, etc.)
- `other` - Other payment methods

## Endpoints

### 1. List Expenses

**GET** `/expenses`

Retrieve expenses with optional filters and pagination.

**Query Parameters:**
- `start_date` (optional): Filter by start date (ISO 8601 format)
- `end_date` (optional): Filter by end date (ISO 8601 format)
- `category` (optional): Filter by category
- `min_amount` (optional): Filter by minimum amount
- `max_amount` (optional): Filter by maximum amount
- `search` (optional): Search in description, merchant, subcategory
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 50, max: 100)

**Example Request:**
```
GET /expenses?category=food&start_date=2025-06-01&end_date=2025-06-30&page=1&limit=20
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "amount": 12.50,
      "currency": "USD",
      "category": "food",
      "subcategory": "coffee",
      "merchant": "Starbucks",
      "description": "Morning coffee",
      "date": "2025-06-23T08:00:00Z",
      "payment_method": "credit_card",
      "receipt_url": "/uploads/receipts/uuid.jpg",
      "is_recurring": false,
      "recurrence_rule": null,
      "tags": ["morning", "caffeine"],
      "created_at": "2025-06-23T08:05:00Z",
      "updated_at": "2025-06-23T08:05:00Z"
    }
  ],
  "message": "Retrieved 1 expenses",
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "pages": 1
  }
}
```

### 2. Create New Expense

**POST** `/expenses`

Create a new expense entry.

**Request Body:**
```json
{
  "amount": 12.50,
  "currency": "USD",
  "category": "food",
  "subcategory": "coffee",
  "merchant": "Starbucks",
  "description": "Morning coffee",
  "date": "2025-06-23T08:00:00Z",
  "payment_method": "credit_card",
  "is_recurring": false,
  "recurrence_rule": null,
  "tags": ["morning", "caffeine"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "amount": 12.50,
    "currency": "USD",
    "category": "food",
    "subcategory": "coffee",
    "merchant": "Starbucks",
    "description": "Morning coffee",
    "date": "2025-06-23T08:00:00Z",
    "payment_method": "credit_card",
    "receipt_url": null,
    "is_recurring": false,
    "recurrence_rule": null,
    "tags": ["morning", "caffeine"],
    "created_at": "2025-06-23T08:05:00Z",
    "updated_at": "2025-06-23T08:05:00Z"
  },
  "message": "Expense created successfully"
}
```

### 3. Get Specific Expense

**GET** `/expenses/{expense_id}`

Retrieve a specific expense by ID.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "amount": 12.50,
    "currency": "USD",
    "category": "food",
    "subcategory": "coffee",
    "merchant": "Starbucks",
    "description": "Morning coffee",
    "date": "2025-06-23T08:00:00Z",
    "payment_method": "credit_card",
    "receipt_url": "/uploads/receipts/uuid.jpg",
    "is_recurring": false,
    "recurrence_rule": null,
    "tags": ["morning", "caffeine"],
    "created_at": "2025-06-23T08:05:00Z",
    "updated_at": "2025-06-23T08:05:00Z"
  },
  "message": "Expense retrieved successfully"
}
```

### 4. Update Expense

**PUT** `/expenses/{expense_id}`

Update an existing expense.

**Request Body:**
```json
{
  "amount": 15.00,
  "description": "Large morning coffee",
  "tags": ["morning", "caffeine", "large"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "amount": 15.00,
    "currency": "USD",
    "category": "food",
    "subcategory": "coffee",
    "merchant": "Starbucks",
    "description": "Large morning coffee",
    "date": "2025-06-23T08:00:00Z",
    "payment_method": "credit_card",
    "receipt_url": "/uploads/receipts/uuid.jpg",
    "is_recurring": false,
    "recurrence_rule": null,
    "tags": ["morning", "caffeine", "large"],
    "created_at": "2025-06-23T08:05:00Z",
    "updated_at": "2025-06-23T10:15:00Z"
  },
  "message": "Expense updated successfully"
}
```

### 5. Delete Expense

**DELETE** `/expenses/{expense_id}`

Delete an expense.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "amount": 15.00,
    "currency": "USD",
    "category": "food",
    "subcategory": "coffee",
    "merchant": "Starbucks",
    "description": "Large morning coffee",
    "date": "2025-06-23T08:00:00Z",
    "payment_method": "credit_card",
    "receipt_url": "/uploads/receipts/uuid.jpg",
    "is_recurring": false,
    "recurrence_rule": null,
    "tags": ["morning", "caffeine", "large"],
    "created_at": "2025-06-23T08:05:00Z",
    "updated_at": "2025-06-23T10:15:00Z"
  },
  "message": "Expense deleted successfully"
}
```

### 6. Parse Natural Language Expense

**POST** `/expenses/parse`

Parse natural language text into expense data using AI.

**Request Body:**
```json
{
  "text": "I spent $12.50 on coffee at Starbucks this morning"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "amount": 12.50,
    "currency": "USD",
    "category": "food",
    "description": "I spent $12.50 on coffee at Starbucks this morning",
    "date": "2025-06-23T08:00:00Z"
  },
  "message": "Text parsed successfully"
}
```

### 7. Get Spending Summary

**GET** `/expenses/summary`

Get spending summary with category breakdown for a period.

**Query Parameters:**
- `start_date` (optional): Summary start date
- `end_date` (optional): Summary end date

**Response:**
```json
{
  "success": true,
  "data": {
    "total_amount": 250.75,
    "total_count": 15,
    "average_amount": 16.72,
    "categories": [
      {
        "category": "food",
        "total_amount": 125.50,
        "count": 8,
        "percentage": 50.05
      },
      {
        "category": "transport",
        "total_amount": 75.25,
        "count": 4,
        "percentage": 30.01
      }
    ],
    "period_start": "2025-06-01T00:00:00Z",
    "period_end": "2025-06-30T23:59:59Z"
  },
  "message": "Expense summary retrieved successfully"
}
```

### 8. Get Expense Categories

**GET** `/expenses/categories`

Get expense categories with totals.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "category": "food",
      "total_amount": 125.50,
      "count": 8,
      "percentage": 50.05
    },
    {
      "category": "transport",
      "total_amount": 75.25,
      "count": 4,
      "percentage": 30.01
    }
  ],
  "message": "Categories retrieved successfully"
}
```

### 9. Get Monthly Expenses

**GET** `/expenses/monthly/{year}/{month}`

Get expenses for a specific month.

**Path Parameters:**
- `year`: Year (e.g., 2025)
- `month`: Month (1-12)

**Response:**
```json
{
  "success": true,
  "data": {
    "year": 2025,
    "month": 6,
    "total_amount": 250.75,
    "count": 15,
    "categories": [
      {
        "category": "food",
        "total_amount": 125.50,
        "count": 8,
        "percentage": 50.05
      }
    ]
  },
  "message": "Monthly expenses for 6/2025 retrieved successfully"
}
```

### 10. Upload Receipt

**POST** `/expenses/{expense_id}/receipt`

Upload receipt image for an expense.

**Request:**
- Content-Type: `multipart/form-data`
- Body: File upload with key `file`

**Supported formats:** JPG, JPEG, PNG, GIF, WebP
**Maximum file size:** 5MB

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "amount": 12.50,
    "currency": "USD",
    "category": "food",
    "subcategory": "coffee",
    "merchant": "Starbucks",
    "description": "Morning coffee",
    "date": "2025-06-23T08:00:00Z",
    "payment_method": "credit_card",
    "receipt_url": "/uploads/receipts/new-uuid.jpg",
    "is_recurring": false,
    "recurrence_rule": null,
    "tags": ["morning", "caffeine"],
    "created_at": "2025-06-23T08:05:00Z",
    "updated_at": "2025-06-23T10:30:00Z"
  },
  "message": "Receipt uploaded successfully"
}
```

### 11. Get Recurring Expenses

**GET** `/expenses/recurring`

Get all recurring expenses.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "amount": 50.00,
      "currency": "USD",
      "category": "bills",
      "subcategory": "internet",
      "merchant": "ISP Provider",
      "description": "Monthly internet bill",
      "date": "2025-06-01T00:00:00Z",
      "payment_method": "bank_transfer",
      "receipt_url": null,
      "is_recurring": true,
      "recurrence_rule": "FREQ=MONTHLY;INTERVAL=1",
      "tags": ["bills", "monthly"],
      "created_at": "2025-06-01T00:00:00Z",
      "updated_at": "2025-06-01T00:00:00Z"
    }
  ],
  "message": "Retrieved 1 recurring expenses"
}
```

### 12. Bulk Import Expenses

**POST** `/expenses/bulk`

Import multiple expenses at once.

**Request Body:**
```json
{
  "expenses": [
    {
      "amount": 12.50,
      "currency": "USD",
      "category": "food",
      "description": "Coffee",
      "date": "2025-06-23T08:00:00Z"
    },
    {
      "amount": 25.00,
      "currency": "USD",
      "category": "transport",
      "description": "Taxi",
      "date": "2025-06-23T09:00:00Z"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid1",
      "user_id": "uuid",
      "amount": 12.50,
      "currency": "USD",
      "category": "food",
      "description": "Coffee",
      "date": "2025-06-23T08:00:00Z",
      "created_at": "2025-06-23T10:00:00Z",
      "updated_at": "2025-06-23T10:00:00Z"
    },
    {
      "id": "uuid2",
      "user_id": "uuid",
      "amount": 25.00,
      "currency": "USD",
      "category": "transport",
      "description": "Taxi",
      "date": "2025-06-23T09:00:00Z",
      "created_at": "2025-06-23T10:00:00Z",
      "updated_at": "2025-06-23T10:00:00Z"
    }
  ],
  "message": "Successfully imported 2 expenses"
}
```

### 13. Export Expenses

**GET** `/expenses/export`

Export expenses to CSV or JSON format.

**Query Parameters:**
- `format` (optional): Export format ("csv" or "json", default: "csv")
- `start_date` (optional): Export start date
- `end_date` (optional): Export end date

**CSV Response:**
```json
{
  "success": true,
  "data": "ID,Amount,Currency,Category,Subcategory,Merchant,Description,Date,Payment Method,Is Recurring,Tags,Created At\nuuid,12.50,USD,food,coffee,Starbucks,Morning coffee,2025-06-23T08:00:00Z,credit_card,False,\"morning, caffeine\",2025-06-23T08:05:00Z",
  "message": "Exported 1 expenses to CSV"
}
```

**JSON Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "amount": 12.50,
      "currency": "USD",
      "category": "food",
      "subcategory": "coffee",
      "merchant": "Starbucks",
      "description": "Morning coffee",
      "date": "2025-06-23T08:00:00Z",
      "payment_method": "credit_card",
      "receipt_url": "/uploads/receipts/uuid.jpg",
      "is_recurring": false,
      "recurrence_rule": null,
      "tags": ["morning", "caffeine"],
      "created_at": "2025-06-23T08:05:00Z",
      "updated_at": "2025-06-23T08:05:00Z"
    }
  ],
  "message": "Exported 1 expenses to JSON"
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": {}
  }
}
```

Common error codes:
- `401`: Unauthorized (invalid or missing token)
- `403`: Forbidden (user account deactivated)
- `404`: Not Found (expense not found)
- `400`: Bad Request (validation errors)
- `500`: Internal Server Error

## Usage Examples

### Track Daily Coffee Expense
```bash
curl -X POST "http://localhost:8000/expenses" \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 4.50,
    "currency": "USD",
    "category": "food",
    "subcategory": "coffee",
    "merchant": "Local Cafe",
    "description": "Morning latte",
    "date": "2025-06-23T08:30:00Z",
    "payment_method": "credit_card",
    "tags": ["morning", "caffeine"]
  }'
```

### Get Monthly Food Expenses
```bash
curl -X GET "http://localhost:8000/expenses?category=food&start_date=2025-06-01&end_date=2025-06-30" \
  -H "Authorization: Bearer your_jwt_token"
```

### Parse Natural Language
```bash
curl -X POST "http://localhost:8000/expenses/parse" \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Paid $35 for dinner at Italian restaurant last night"
  }'
```

### Get Spending Summary
```bash
curl -X GET "http://localhost:8000/expenses/summary?start_date=2025-06-01&end_date=2025-06-30" \
  -H "Authorization: Bearer your_jwt_token"
```

## Dashboard Analytics Endpoints

The following endpoints provide data visualization and analytics specifically designed for dashboard widgets and charts.

### 14. Get Total Spend Dashboard Data

**GET** `/expenses/dashboard/total-spend`

Get current month total spend vs previous month with percentage change for dashboard display.

**Response:**
```json
{
  "success": true,
  "data": {
    "current_month": 450.75,
    "previous_month": 380.25,
    "percentage_change": 18.53,
    "change_direction": "increase"
  },
  "message": "Total spend data retrieved successfully"
}
```

**Response Fields:**
- `current_month`: Total spending for the current month
- `previous_month`: Total spending for the previous month
- `percentage_change`: Percentage change between months (positive for increase, negative for decrease)
- `change_direction`: Direction of change ("increase", "decrease", or "same")

### 15. Get Category Breakdown Dashboard Data

**GET** `/expenses/dashboard/category-breakdown`

Get spending breakdown by category for pie chart visualization.

**Query Parameters:**
- `period` (optional): Time period for breakdown
  - `current_month` (default): Current month only
  - `last_30_days`: Last 30 days
  - `current_year`: Current year to date

**Example Request:**
```
GET /expenses/dashboard/category-breakdown?period=current_month
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "category": "food",
      "amount": 225.50,
      "percentage": 50.06,
      "transaction_count": 18
    },
    {
      "category": "transport",
      "amount": 135.25,
      "percentage": 30.01,
      "transaction_count": 8
    },
    {
      "category": "entertainment",
      "amount": 90.00,
      "percentage": 19.98,
      "transaction_count": 5
    }
  ],
  "message": "Category breakdown for current_month retrieved successfully"
}
```

**Response Fields:**
- `category`: Expense category name
- `amount`: Total amount spent in this category
- `percentage`: Percentage of total spending
- `transaction_count`: Number of transactions in this category

### 16. Get Category Trend Dashboard Data

**GET** `/expenses/dashboard/category-trend`

Get category spending trend over time showing how each category's share evolves monthly.

**Query Parameters:**
- `months` (optional): Number of months to analyze (default: 6, min: 3, max: 24)

**Example Request:**
```
GET /expenses/dashboard/category-trend?months=6
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "month": "2025-01",
      "category": "food",
      "amount": 180.25,
      "percentage": 45.12
    },
    {
      "month": "2025-01",
      "category": "transport",
      "amount": 120.50,
      "percentage": 30.15
    },
    {
      "month": "2025-02",
      "category": "food",
      "amount": 195.75,
      "percentage": 48.25
    },
    {
      "month": "2025-02",
      "category": "transport",
      "amount": 110.25,
      "percentage": 27.18
    }
  ],
  "message": "Category trend data for last 6 months retrieved successfully"
}
```

**Response Fields:**
- `month`: Month in YYYY-MM format
- `category`: Expense category name
- `amount`: Total amount spent in this category for the month
- `percentage`: Percentage of total spending for that month

### 17. Get Spend Trend Dashboard Data

**GET** `/expenses/dashboard/spend-trend`

Get spending trend over time for line chart visualization.

**Query Parameters:**
- `period` (optional): Time period granularity
  - `daily` (default): Daily aggregation
  - `weekly`: Weekly aggregation
  - `monthly`: Monthly aggregation
- `days` (optional): Number of days to analyze (default: 30, min: 7, max: 365)

**Example Request:**
```
GET /expenses/dashboard/spend-trend?period=daily&days=30
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "date": "2025-06-01",
      "amount": 45.25,
      "transaction_count": 3
    },
    {
      "date": "2025-06-02",
      "amount": 23.50,
      "transaction_count": 2
    },
    {
      "date": "2025-06-03",
      "amount": 67.80,
      "transaction_count": 5
    }
  ],
  "message": "Spend trend data (daily) retrieved successfully"
}
```

**Response Fields:**
- `date`: Date in format depending on period (YYYY-MM-DD for daily, YYYY-WXX for weekly, YYYY-MM for monthly)
- `amount`: Total amount spent for that period
- `transaction_count`: Number of transactions for that period

### 18. Get Top Transactions Dashboard Data

**GET** `/expenses/dashboard/top-transactions`

Get top transactions by amount for specified period.

**Query Parameters:**
- `period` (optional): Time period for top transactions
  - `weekly`: Last week
  - `monthly` (default): Last month
  - `yearly`: Last year
- `limit` (optional): Number of top transactions to return (default: 5, min: 3, max: 10)

**Example Request:**
```
GET /expenses/dashboard/top-transactions?period=monthly&limit=5
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-1",
      "amount": 125.00,
      "category": "shopping",
      "merchant": "Amazon",
      "description": "Home office supplies",
      "date": "2025-06-15T14:30:00Z"
    },
    {
      "id": "uuid-2",
      "amount": 89.50,
      "category": "food",
      "merchant": "Fine Dining Restaurant",
      "description": "Anniversary dinner",
      "date": "2025-06-12T19:00:00Z"
    },
    {
      "id": "uuid-3",
      "amount": 75.25,
      "category": "transport",
      "merchant": "Gas Station",
      "description": "Fuel for road trip",
      "date": "2025-06-10T08:15:00Z"
    }
  ],
  "message": "Top 5 transactions (monthly) retrieved successfully"
}
```

**Response Fields:**
- `id`: Transaction UUID
- `amount`: Transaction amount
- `category`: Expense category
- `merchant`: Merchant name (optional)
- `description`: Transaction description (optional)
- `date`: Transaction date

## Dashboard Usage Examples

### Get Current Month Summary
```bash
curl -X GET "http://localhost:8000/expenses/dashboard/total-spend" \
  -H "Authorization: Bearer your_jwt_token"
```

### Get Category Breakdown for Pie Chart
```bash
curl -X GET "http://localhost:8000/expenses/dashboard/category-breakdown?period=current_month" \
  -H "Authorization: Bearer your_jwt_token"
```

### Get Daily Spending Trend for Line Chart
```bash
curl -X GET "http://localhost:8000/expenses/dashboard/spend-trend?period=daily&days=30" \
  -H "Authorization: Bearer your_jwt_token"
```

### Get Category Evolution Over 6 Months
```bash
curl -X GET "http://localhost:8000/expenses/dashboard/category-trend?months=6" \
  -H "Authorization: Bearer your_jwt_token"
```

### Get Top 5 Monthly Transactions
```bash
curl -X GET "http://localhost:8000/expenses/dashboard/top-transactions?period=monthly&limit=5" \
  -H "Authorization: Bearer your_jwt_token"
```

## Dashboard Data Models

### Dashboard Response Schemas

#### TotalSpendData
```json
{
  "current_month": 450.75,
  "previous_month": 380.25,
  "percentage_change": 18.53,
  "change_direction": "increase"
}
```

#### CategoryBreakdownItem
```json
{
  "category": "food",
  "amount": 225.50,
  "percentage": 50.06,
  "transaction_count": 18
}
```

#### CategoryTrendMonth
```json
{
  "month": "2025-01",
  "category": "food",
  "amount": 180.25,
  "percentage": 45.12
}
```

#### SpendTrendData
```json
{
  "date": "2025-06-01",
  "amount": 45.25,
  "transaction_count": 3
}
```

#### TopTransactionData
```json
{
  "id": "uuid",
  "amount": 125.00,
  "category": "shopping",
  "merchant": "Amazon",
  "description": "Home office supplies",
  "date": "2025-06-15T14:30:00Z"
}
```

## Frontend Integration

These dashboard endpoints are designed to provide ready-to-use data for common dashboard visualizations:

1. **Total Spend Card**: Use `/dashboard/total-spend` for a single-value card showing current month total with percentage change indicator
2. **Category Pie Chart**: Use `/dashboard/category-breakdown` with appropriate period for proportional spending visualization
3. **Spending Line Chart**: Use `/dashboard/spend-trend` with desired granularity for trend visualization
4. **Category Trend Chart**: Use `/dashboard/category-trend` for stacked area or multi-line charts showing category evolution
5. **Top Transactions List**: Use `/dashboard/top-transactions` for highlighting significant expenses

All endpoints return data optimized for chart libraries like Chart.js, D3.js, or Recharts.

## Testing

1. Start the server:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. Visit the interactive documentation:
   ```
   http://localhost:8000/docs
   ```

3. Test with authentication:
   - First, create a user account and login to get a JWT token
   - Use the token in the Authorization header for all expense endpoints

## Integration with AI Services

The `/expenses/parse` endpoint provides a foundation for integrating with AI services like Google Gemini for natural language processing. Currently, it includes a mock implementation that can be replaced with actual AI service integration.

## File Structure

```
backend/
├── app/
│   ├── routers/
│   │   └── expenses.py              # Expense endpoints
│   ├── services/
│   │   └── expenses.py              # Business logic
│   ├── schemas/
│   │   └── expenses.py              # Expense schemas
│   ├── models/
│   │   └── models.py                # Updated with Expense model
│   └── utils/
│       └── upload.py                # Receipt upload utilities
└── uploads/
    └── receipts/                    # Receipt storage directory
```
