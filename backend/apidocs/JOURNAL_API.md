# Journal API Documentation

This document provides detailed information about the Journal API endpoints in the LIN application.

## Base URL
```
http://localhost:8000/journal
```

## Authentication
All endpoints require Bearer token authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

---

## Endpoints

### 1. List Journal Entries
**GET** `/journal/`

Retrieve journal entries with optional filters and pagination.

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| start_date | datetime | No | Filter by entries created after this date |
| end_date | datetime | No | Filter by entries created before this date |
| mood | string | No | Filter by mood (very_happy, happy, neutral, sad, very_sad, angry, excited, anxious, grateful) |
| search | string | No | Search in title, content, and summary |
| page | integer | No | Page number (default: 1) |
| limit | integer | No | Items per page (default: 50, max: 100) |

#### Response
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "title": "Morning Reflections",
      "content": "Had a great morning workout...",
      "mood": "happy",
      "sentiment_score": 0.8,
      "keywords": ["workout", "morning", "energy"],
      "summary": "User had a positive morning workout experience",
      "weather": "Sunny, 72°F",
      "location": "Home",
      "created_at": "2025-07-02T10:30:00Z",
      "updated_at": "2025-07-02T10:30:00Z"
    }
  ],
  "message": "Journal entries retrieved successfully",
  "meta": {
    "total": 25,
    "page": 1,
    "limit": 50,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

---

### 2. Create Journal Entry
**POST** `/journal/`

Create a new journal entry with AI analysis.

#### Request Body
```json
{
  "title": "Optional entry title",
  "content": "Required entry content (max 10,000 chars)",
  "mood": "happy",
  "weather": "Sunny, 72°F",
  "location": "Home"
}
```

#### Response
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "title": "Optional entry title",
    "content": "Required entry content",
    "mood": "happy",
    "sentiment_score": null,
    "keywords": null,
    "summary": null,
    "weather": "Sunny, 72°F",
    "location": "Home",
    "created_at": "2025-07-02T10:30:00Z",
    "updated_at": "2025-07-02T10:30:00Z"
  },
  "message": "Journal entry created successfully",
  "meta": {
    "timestamp": "2025-07-02T10:30:00Z"
  }
}
```

---

### 3. Get Journal Entry
**GET** `/journal/{entry_id}`

Retrieve a specific journal entry by ID.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| entry_id | UUID | Yes | Journal entry ID |

#### Response
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "title": "Entry title",
    "content": "Entry content",
    "mood": "happy",
    "sentiment_score": 0.8,
    "keywords": ["keyword1", "keyword2"],
    "summary": "AI-generated summary",
    "weather": "Sunny",
    "location": "Home",
    "created_at": "2025-07-02T10:30:00Z",
    "updated_at": "2025-07-02T10:30:00Z"
  },
  "message": "Journal entry retrieved successfully",
  "meta": {
    "timestamp": "2025-07-02T10:30:00Z"
  }
}
```

---

### 4. Update Journal Entry
**PUT** `/journal/{entry_id}`

Update an existing journal entry.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| entry_id | UUID | Yes | Journal entry ID |

#### Request Body
```json
{
  "title": "Updated title",
  "content": "Updated content",
  "mood": "very_happy",
  "weather": "Updated weather",
  "location": "Updated location"
}
```

#### Response
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "title": "Updated title",
    "content": "Updated content",
    "mood": "very_happy",
    "sentiment_score": 0.9,
    "keywords": ["updated", "keywords"],
    "summary": "Updated AI summary",
    "weather": "Updated weather",
    "location": "Updated location",
    "created_at": "2025-07-02T10:30:00Z",
    "updated_at": "2025-07-02T11:00:00Z"
  },
  "message": "Journal entry updated successfully",
  "meta": {
    "timestamp": "2025-07-02T11:00:00Z"
  }
}
```

---

### 5. Delete Journal Entry
**DELETE** `/journal/{entry_id}`

Delete a journal entry.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| entry_id | UUID | Yes | Journal entry ID |

#### Response
```json
{
  "success": true,
  "message": "Journal entry deleted successfully",
  "meta": {
    "timestamp": "2025-07-02T11:00:00Z"
  }
}
```

---

### 6. Parse Natural Language
**POST** `/journal/parse`

Parse natural language input into journal entry data.

#### Request Body
```json
{
  "text": "Today was an amazing day! I went for a run in the park and felt really energized."
}
```

#### Response
```json
{
  "success": true,
  "data": {
    "title": null,
    "content": "Today was an amazing day! I went for a run in the park and felt really energized.",
    "mood": null,
    "weather": null,
    "location": null
  },
  "message": "Text parsed successfully",
  "meta": {
    "timestamp": "2025-07-02T11:00:00Z"
  }
}
```

---

### 7. Trigger AI Analysis
**POST** `/journal/analyze`

Trigger AI analysis for existing journal entries.

#### Request Body
```json
{
  "entry_ids": ["uuid1", "uuid2"]  // Optional: if not provided, analyzes all entries
}
```

#### Response
```json
{
  "success": true,
  "message": "Analysis triggered for 2 entries",
  "meta": {
    "analyzed_entries": 2,
    "timestamp": "2025-07-02T11:00:00Z"
  }
}
```

---

### 8. Get Journal Statistics
**GET** `/journal/stats`

Get journaling statistics and metrics.

#### Response
```json
{
  "success": true,
  "data": {
    "total_entries": 25,
    "entries_this_month": 8,
    "mood_distribution": {
      "happy": 10,
      "neutral": 8,
      "excited": 5,
      "grateful": 2
    },
    "average_sentiment": 0.6,
    "longest_streak": 7
  },
  "message": "Journal statistics retrieved successfully",
  "meta": {
    "timestamp": "2025-07-02T11:00:00Z"
  }
}
```

---

### 9. Get Mood Trends
**GET** `/journal/mood-trends`

Get mood trends over time.

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| days | integer | No | Number of days to analyze (default: 30, max: 365) |

#### Response
```json
{
  "success": true,
  "data": {
    "trends": {
      "2025-07-01": [
        {
          "mood": "happy",
          "avg_sentiment": 0.8
        }
      ],
      "2025-07-02": [
        {
          "mood": "excited",
          "avg_sentiment": 0.9
        }
      ]
    },
    "period_days": 30,
    "start_date": "2025-06-02",
    "end_date": "2025-07-02"
  },
  "message": "Mood trends retrieved successfully",
  "meta": {
    "timestamp": "2025-07-02T11:00:00Z"
  }
}
```

---

## Data Models

### JournalEntry
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| user_id | UUID | Owner of the entry |
| title | string | Optional entry title (max 255 chars) |
| content | string | Entry content (required, max 10,000 chars) |
| mood | enum | Optional mood (very_happy, happy, neutral, sad, very_sad, angry, excited, anxious, grateful) |
| sentiment_score | float | AI-calculated sentiment (-1.0 to 1.0) |
| keywords | array | AI-extracted keywords |
| summary | string | AI-generated summary |
| weather | string | Optional weather information |
| location | string | Optional location |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last update timestamp |

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "content": ["Field required"]
    }
  }
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required"
  }
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Journal entry not found"
  }
}
```

### 422 Unprocessable Entity
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation error",
    "details": {
      "content": ["String should have at most 10000 characters"]
    }
  }
}
```

---

## Notes

1. **AI Analysis**: Currently placeholder functionality. Will be implemented with Google Gemini integration.

2. **Sentiment Score**: Range from -1.0 (very negative) to 1.0 (very positive).

3. **Keywords**: AI-extracted keywords stored as JSON array.

4. **Search**: Searches across title, content, and summary fields (case-insensitive).

5. **Pagination**: Default limit is 50 entries per page, maximum is 100.

6. **Date Filters**: Use ISO 8601 format for date parameters (e.g., "2025-07-02T10:30:00Z").

7. **Mood Values**: 
   - very_happy
   - happy  
   - neutral
   - sad
   - very_sad
   - angry
   - excited
   - anxious
   - grateful
