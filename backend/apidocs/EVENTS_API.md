# Events API Documentation

This document describes all the Events API endpoints available in the LIN: AI-Powered Personal Life Manager.

## Base URL
```
http://localhost:8000/events
```

## Authentication
All endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Event Model

### Event Object Structure
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "description": "string (optional)",
  "start_time": "datetime (ISO 8601)",
  "end_time": "datetime (ISO 8601)",
  "location": "string (optional)",
  "tags": ["string"] (optional),
  "is_all_day": "boolean (default: false)",
  "reminder_minutes": "integer (optional, >= 0)",
  "recurrence_rule": "string (optional, RRULE format)",
  "color": "string (optional, hex color #RRGGBB)",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

## API Endpoints

### 1. List Events
Get a list of events with optional filtering.

**Endpoint:** `GET /events`

**Query Parameters:**
- `start_date` (optional): Filter events starting from this date (ISO 8601)
- `end_date` (optional): Filter events ending before this date (ISO 8601)
- `tags` (optional): Filter by tags (can specify multiple)
- `search` (optional): Search in title, description, and location
- `page` (optional): Page number (default: 1, min: 1)
- `limit` (optional): Items per page (default: 50, min: 1, max: 100)

**Example Request:**
```bash
GET /events?start_date=2025-06-24T00:00:00Z&tags=work&tags=meeting&page=1&limit=10
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "33333333-3333-3333-3333-333333333333",
      "user_id": "11111111-1111-1111-1111-111111111111",
      "title": "Team Standup",
      "description": "Daily team standup meeting",
      "start_time": "2025-06-25T09:00:00+06:00",
      "end_time": "2025-06-25T09:30:00+06:00",
      "location": "Conference Room A",
      "tags": ["work", "meeting", "daily"],
      "is_all_day": false,
      "reminder_minutes": 15,
      "recurrence_rule": "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR",
      "color": "#4CAF50",
      "created_at": "2025-06-24T10:30:00Z",
      "updated_at": "2025-06-24T10:30:00Z"
    }
  ],
  "message": "Events retrieved successfully",
  "meta": {
    "total": 15,
    "page": 1,
    "limit": 10,
    "pages": 2,
    "timestamp": "2025-06-24T10:30:00Z"
  }
}
```

### 2. Create Event
Create a new event.

**Endpoint:** `POST /events`

**Request Body:**
```json
{
  "title": "Team Meeting",
  "description": "Weekly team sync meeting",
  "start_time": "2025-06-25T14:00:00+06:00",
  "end_time": "2025-06-25T15:00:00+06:00",
  "location": "Conference Room B",
  "tags": ["work", "meeting"],
  "is_all_day": false,
  "reminder_minutes": 30,
  "color": "#4CAF50"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "66666666-6666-6666-6666-666666666666",
    "user_id": "11111111-1111-1111-1111-111111111111",
    "title": "Team Meeting",
    "description": "Weekly team sync meeting",
    "start_time": "2025-06-25T14:00:00+06:00",
    "end_time": "2025-06-25T15:00:00+06:00",
    "location": "Conference Room B",
    "tags": ["work", "meeting"],
    "is_all_day": false,
    "reminder_minutes": 30,
    "recurrence_rule": null,
    "color": "#4CAF50",
    "created_at": "2025-06-24T10:30:00Z",
    "updated_at": "2025-06-24T10:30:00Z"
  },
  "message": "Event created successfully",
  "meta": {
    "timestamp": "2025-06-24T10:30:00Z"
  }
}
```

### 3. Get Specific Event
Retrieve a specific event by ID.

**Endpoint:** `GET /events/{event_id}`

**Example Request:**
```bash
GET /events/33333333-3333-3333-3333-333333333333
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "33333333-3333-3333-3333-333333333333",
    "user_id": "11111111-1111-1111-1111-111111111111",
    "title": "Team Standup",
    "description": "Daily team standup meeting",
    "start_time": "2025-06-25T09:00:00+06:00",
    "end_time": "2025-06-25T09:30:00+06:00",
    "location": "Conference Room A",
    "tags": ["work", "meeting", "daily"],
    "is_all_day": false,
    "reminder_minutes": 15,
    "recurrence_rule": "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR",
    "color": "#4CAF50",
    "created_at": "2025-06-24T10:30:00Z",
    "updated_at": "2025-06-24T10:30:00Z"
  },
  "message": "Event retrieved successfully",
  "meta": {
    "timestamp": "2025-06-24T10:30:00Z"
  }
}
```

### 4. Update Event
Update an existing event.

**Endpoint:** `PUT /events/{event_id}`

**Request Body (all fields optional):**
```json
{
  "title": "Updated Team Meeting",
  "description": "Updated description",
  "location": "New Conference Room",
  "tags": ["work", "meeting", "updated"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "33333333-3333-3333-3333-333333333333",
    "user_id": "11111111-1111-1111-1111-111111111111",
    "title": "Updated Team Meeting",
    "description": "Updated description",
    "start_time": "2025-06-25T09:00:00+06:00",
    "end_time": "2025-06-25T09:30:00+06:00",
    "location": "New Conference Room",
    "tags": ["work", "meeting", "updated"],
    "is_all_day": false,
    "reminder_minutes": 15,
    "recurrence_rule": "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR",
    "color": "#4CAF50",
    "created_at": "2025-06-24T10:30:00Z",
    "updated_at": "2025-06-24T10:35:00Z"
  },
  "message": "Event updated successfully",
  "meta": {
    "timestamp": "2025-06-24T10:35:00Z"
  }
}
```

### 5. Delete Event
Delete an existing event.

**Endpoint:** `DELETE /events/{event_id}`

**Example Request:**
```bash
DELETE /events/33333333-3333-3333-3333-333333333333
```

**Response:**
```json
{
  "success": true,
  "message": "Event deleted successfully",
  "meta": {
    "timestamp": "2025-06-24T10:40:00Z"
  }
}
```

### 6. Get Calendar View
Get calendar view for a specific month.

**Endpoint:** `GET /events/calendar/{year}/{month}`

**Path Parameters:**
- `year`: Year (1900-3000)
- `month`: Month (1-12)

**Example Request:**
```bash
GET /events/calendar/2025/6
```

**Response:**
```json
{
  "success": true,
  "data": {
    "year": 2025,
    "month": 6,
    "month_name": "June",
    "calendar_grid": [
      [null, null, null, null, null, null, 1],
      [2, 3, 4, 5, 6, 7, 8],
      [9, 10, 11, 12, 13, 14, 15],
      [16, 17, 18, 19, 20, 21, 22],
      [23, 24, 25, 26, 27, 28, 29],
      [30, null, null, null, null, null, null]
    ],
    "events": [
      {
        "id": "33333333-3333-3333-3333-333333333333",
        "title": "Team Standup",
        "description": "Daily team standup meeting",
        "start_time": "2025-06-25T09:00:00+06:00",
        "end_time": "2025-06-25T09:30:00+06:00",
        "location": "Conference Room A",
        "tags": ["work", "meeting", "daily"],
        "is_all_day": false,
        "color": "#4CAF50"
      }
    ],
    "events_by_date": {
      "2025-06-25": [
        {
          "id": "33333333-3333-3333-3333-333333333333",
          "title": "Team Standup",
          "description": "Daily team standup meeting",
          "start_time": "2025-06-25T09:00:00+06:00",
          "end_time": "2025-06-25T09:30:00+06:00",
          "location": "Conference Room A",
          "tags": ["work", "meeting", "daily"],
          "is_all_day": false,
          "color": "#4CAF50"
        }
      ]
    }
  },
  "message": "Calendar view retrieved successfully",
  "meta": {
    "timestamp": "2025-06-24T10:30:00Z"
  }
}
```

### 7. Get Upcoming Events
Get upcoming events for the next N days.

**Endpoint:** `GET /events/upcoming`

**Query Parameters:**
- `days` (optional): Number of days to look ahead (default: 7, min: 1, max: 30)

**Example Request:**
```bash
GET /events/upcoming?days=14
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "33333333-3333-3333-3333-333333333333",
      "user_id": "11111111-1111-1111-1111-111111111111",
      "title": "Team Standup",
      "description": "Daily team standup meeting",
      "start_time": "2025-06-25T09:00:00+06:00",
      "end_time": "2025-06-25T09:30:00+06:00",
      "location": "Conference Room A",
      "tags": ["work", "meeting", "daily"],
      "is_all_day": false,
      "reminder_minutes": 15,
      "recurrence_rule": "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR",
      "color": "#4CAF50",
      "created_at": "2025-06-24T10:30:00Z",
      "updated_at": "2025-06-24T10:30:00Z"
    }
  ],
  "message": "Upcoming events retrieved successfully",
  "meta": {
    "total": 5,
    "days": 14,
    "start_date": "2025-06-24T10:30:00Z",
    "end_date": "2025-07-08T10:30:00Z",
    "timestamp": "2025-06-24T10:30:00Z"
  }
}
```

### 8. Parse Natural Language
Parse natural language text into event data.

**Endpoint:** `POST /events/parse`

**Request Body:**
```json
{
  "text": "Lunch with Sarah tomorrow at noon"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "title": "Lunch with Sarah tomorrow at noon",
    "description": "Lunch with Sarah tomorrow at noon",
    "start_time": "2025-06-25T12:00:00Z",
    "end_time": "2025-06-25T13:00:00Z",
    "location": null,
    "tags": ["food"],
    "is_all_day": false,
    "confidence_score": 0.7
  },
  "message": "Text parsed successfully",
  "meta": {
    "timestamp": "2025-06-24T10:30:00Z"
  }
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {}
  }
}
```

### Common Error Codes:
- `401 UNAUTHORIZED`: Invalid or missing authentication token
- `403 FORBIDDEN`: Access denied
- `404 NOT_FOUND`: Event not found
- `400 BAD_REQUEST`: Invalid request data
- `422 VALIDATION_ERROR`: Request validation failed
- `500 INTERNAL_SERVER_ERROR`: Server error

## Validation Rules

### Event Creation/Update:
- `title`: Required, 1-255 characters
- `start_time`: Required, must be valid datetime
- `end_time`: Required, must be after start_time
- `reminder_minutes`: Optional, must be >= 0
- `color`: Optional, must be valid hex color (#RRGGBB)
- `tags`: Optional, array of strings

## Usage Examples

### Create a recurring meeting:
```bash
curl -X POST "http://localhost:8000/events" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Daily Standup",
    "start_time": "2025-06-25T09:00:00+06:00",
    "end_time": "2025-06-25T09:30:00+06:00",
    "location": "Virtual",
    "tags": ["work", "daily"],
    "reminder_minutes": 15,
    "recurrence_rule": "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR",
    "color": "#4CAF50"
  }'
```

### Get events for current week:
```bash
curl -X GET "http://localhost:8000/events?start_date=2025-06-23T00:00:00Z&end_date=2025-06-29T23:59:59Z" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Search for work meetings:
```bash
curl -X GET "http://localhost:8000/events?search=meeting&tags=work" \
  -H "Authorization: Bearer YOUR_TOKEN"
```
