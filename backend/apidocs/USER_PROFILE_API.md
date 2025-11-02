# User Profile API Documentation

This document describes the User Profile endpoints implemented for the LIN (Life Manager) application.

## Overview

The User Profile endpoints allow authenticated users to manage their personal profile information and preferences. These endpoints follow RESTful conventions and require JWT authentication.

## Authentication

All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. Get Current User Profile

**GET** `/users/me`

Retrieve the profile information of the currently authenticated user.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_verified": false,
    "profile_picture_url": "/uploads/profiles/uuid.jpg",
    "timezone": "UTC",
    "created_at": "2025-06-23T10:00:00Z",
    "updated_at": "2025-06-23T10:00:00Z"
  },
  "message": "User profile retrieved successfully"
}
```

### 2. Update User Profile

**PUT** `/users/me`

Update the profile information of the currently authenticated user.

**Request Body:**
```json
{
  "first_name": "Updated",
  "last_name": "Name",
  "username": "newusername",
  "timezone": "America/New_York"
}
```

**Notes:**
- All fields are optional
- Username must be unique
- Timezone should be a valid IANA timezone

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "username": "newusername",
    "email": "john@example.com",
    "first_name": "Updated",
    "last_name": "Name",
    "is_verified": false,
    "profile_picture_url": "/uploads/profiles/uuid.jpg",
    "timezone": "America/New_York",
    "created_at": "2025-06-23T10:00:00Z",
    "updated_at": "2025-06-23T12:00:00Z"
  },
  "message": "User profile updated successfully"
}
```

### 3. Upload Profile Picture

**POST** `/users/me/avatar`

Upload a new profile picture for the current user.

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
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_verified": false,
    "profile_picture_url": "/uploads/profiles/new-uuid.jpg",
    "timezone": "UTC",
    "created_at": "2025-06-23T10:00:00Z",
    "updated_at": "2025-06-23T12:30:00Z"
  },
  "message": "Profile picture uploaded successfully"
}
```

### 4. Remove Profile Picture

**DELETE** `/users/me/avatar`

Remove the current user's profile picture.

**Response:**
```json
{
  "success": true,
  "message": "Profile picture removed successfully"
}
```

### 5. Get User Preferences

**GET** `/users/me/preferences`

Retrieve the preferences of the currently authenticated user.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "default_task_priority": "medium",
    "default_expense_currency": "USD",
    "notification_settings": {
      "email": true,
      "push": false,
      "in_app": true
    },
    "theme": "auto",
    "language": "en",
    "date_format": "YYYY-MM-DD",
    "time_format": "12h",
    "week_start_day": "monday",
    "ai_insights_enabled": true,
    "created_at": "2025-06-23T10:00:00Z",
    "updated_at": "2025-06-23T10:00:00Z"
  },
  "message": "User preferences retrieved successfully"
}
```

### 6. Update User Preferences

**PUT** `/users/me/preferences`

Update the preferences of the currently authenticated user.

**Request Body:**
```json
{
  "default_task_priority": "high",
  "default_expense_currency": "EUR",
  "notification_settings": {
    "email": true,
    "push": true,
    "in_app": true
  },
  "theme": "dark",
  "language": "en",
  "date_format": "DD/MM/YYYY",
  "time_format": "24h",
  "week_start_day": "sunday",
  "ai_insights_enabled": false
}
```

**Notes:**
- All fields are optional
- Valid values for enums:
  - `default_task_priority`: "low", "medium", "high"
  - `theme`: "light", "dark", "auto"
  - `time_format`: "12h", "24h"
  - `week_start_day`: "monday", "sunday"

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "default_task_priority": "high",
    "default_expense_currency": "EUR",
    "notification_settings": {
      "email": true,
      "push": true,
      "in_app": true
    },
    "theme": "dark",
    "language": "en",
    "date_format": "DD/MM/YYYY",
    "time_format": "24h",
    "week_start_day": "sunday",
    "ai_insights_enabled": false,
    "created_at": "2025-06-23T10:00:00Z",
    "updated_at": "2025-06-23T14:00:00Z"
  },
  "message": "User preferences updated successfully"
}
```

### 7. Delete User Account

**DELETE** `/users/me`

Permanently delete the current user's account and all associated data.

**⚠️ Warning:** This action is irreversible and will delete all user data including profile, preferences, tasks, events, expenses, and journal entries.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_verified": false,
    "profile_picture_url": "/uploads/profiles/uuid.jpg",
    "timezone": "UTC",
    "created_at": "2025-06-23T10:00:00Z",
    "updated_at": "2025-06-23T15:00:00Z"
  },
  "message": "User account deleted successfully"
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
- `404`: Not Found (user not found)
- `400`: Bad Request (validation errors)
- `500`: Internal Server Error

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

3. Use the test script:
   ```bash
   python test_user_profile.py
   ```

## Database Migration

Before using these endpoints, run the database migration:

```bash
python migrate_db.py
```

This will update the existing user table structure and create the user_preferences table.

## File Structure

```
backend/
├── app/
│   ├── routers/
│   │   └── user_profile.py          # User profile endpoints
│   ├── services/
│   │   └── user_profile.py          # Business logic
│   ├── schemas/
│   │   └── users.py                 # Updated with new schemas
│   ├── models/
│   │   └── models.py                # Updated User and UserPreferences models
│   ├── utils/
│   │   └── upload.py                # Profile picture upload utilities
│   └── core/
│       └── security.py              # Authentication helpers
├── migrate_db.py                    # Database migration script
└── test_user_profile.py             # Test script
```
