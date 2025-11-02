# Tasks API Documentation

This document describes the Tasks API endpoints for the LIN application. The Tasks API allows users to manage their to-do items with full CRUD operations, priority management, and natural language parsing.

## Base URL
```
http://localhost:8000/tasks
```

## Authentication
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

---

## Endpoints

### 1. List Tasks
Get a list of tasks with optional filtering and pagination.

**Endpoint:** `GET /tasks/`

**Query Parameters:**
- `status` (optional): Filter by task status (`pending`, `in_progress`, `completed`, `cancelled`)
- `priority` (optional): Filter by priority (`low`, `medium`, `high`)
- `due_date` (optional): Filter by due date (ISO format: `2025-06-24T10:00:00`)
- `tags` (optional): Array of tags to filter by
- `search` (optional): Search text to match in title or description
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 50, max: 100)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/tasks/?status=pending&priority=high&page=1&limit=10" \
  -H "Authorization: Bearer your-jwt-token"
```

**Example Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "user_id": "456e7890-e89b-12d3-a456-426614174000",
      "title": "Complete API Documentation",
      "description": "Write comprehensive API docs",
      "due_date": "2025-06-27T17:00:00Z",
      "priority": "high",
      "status": "pending",
      "is_completed": false,
      "completion_date": null,
      "estimated_duration": 120,
      "actual_duration": null,
      "tags": ["documentation", "api"],
      "parent_task_id": null,
      "created_at": "2025-06-24T10:00:00Z",
      "updated_at": "2025-06-24T10:00:00Z"
    }
  ],
  "message": "Tasks retrieved successfully",
  "meta": {
    "page": 1,
    "limit": 10,
    "total": 25,
    "pages": 3
  }
}
```

---

### 2. Create Task
Create a new task.

**Endpoint:** `POST /tasks/`

**Request Body:**
```json
{
  "title": "Task title (required)",
  "description": "Optional description",
  "due_date": "2025-06-27T17:00:00Z",
  "priority": "medium",
  "status": "pending",
  "estimated_duration": 60,
  "tags": ["tag1", "tag2"],
  "parent_task_id": "parent-task-uuid"
}
```

**Field Descriptions:**
- `title` (required): Task title (1-255 characters)
- `description` (optional): Detailed description
- `due_date` (optional): Due date and time (ISO format)
- `priority` (optional): `low`, `medium`, or `high` (default: `medium`)
- `status` (optional): `pending`, `in_progress`, `completed`, or `cancelled` (default: `pending`)
- `estimated_duration` (optional): Estimated time in minutes
- `tags` (optional): Array of tags
- `parent_task_id` (optional): UUID of parent task for subtasks

**Example Request:**
```bash
curl -X POST "http://localhost:8000/tasks/" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Review quarterly reports",
    "description": "Review Q2 financial reports and prepare summary",
    "due_date": "2025-06-30T17:00:00Z",
    "priority": "high",
    "estimated_duration": 90,
    "tags": ["finance", "quarterly", "reports"]
  }'
```

**Response:** Same structure as individual task object with 201 status code.

---

### 3. Get Task by ID
Retrieve a specific task by its ID.

**Endpoint:** `GET /tasks/{task_id}`

**Example Request:**
```bash
curl -X GET "http://localhost:8000/tasks/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer your-jwt-token"
```

**Response:** Single task object with 200 status code.

---

### 4. Update Task
Update an existing task. Only provided fields will be updated.

**Endpoint:** `PUT /tasks/{task_id}`

**Request Body:** Same as create task, but all fields are optional

**Example Request:**
```bash
curl -X PUT "http://localhost:8000/tasks/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "priority": "low",
    "status": "in_progress",
    "description": "Updated description with more details"
  }'
```

---

### 5. Delete Task
Delete a task and all its subtasks.

**Endpoint:** `DELETE /tasks/{task_id}`

**Example Request:**
```bash
curl -X DELETE "http://localhost:8000/tasks/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer your-jwt-token"
```

**Response:**
```json
{
  "success": true,
  "message": "Task deleted successfully"
}
```

---

### 6. Complete Task
Mark a task as completed and optionally record actual duration.

**Endpoint:** `PATCH /tasks/{task_id}/complete`

**Request Body:**
```json
{
  "actual_duration": 75
}
```

**Example Request:**
```bash
curl -X PATCH "http://localhost:8000/tasks/123e4567-e89b-12d3-a456-426614174000/complete" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{"actual_duration": 75}'
```

**Response:** Updated task object with `status: "completed"`, `is_completed: true`, and `completion_date` set.

---

### 7. Get Today's Tasks
Get all tasks due today that are not completed.

**Endpoint:** `GET /tasks/today`

**Example Request:**
```bash
curl -X GET "http://localhost:8000/tasks/today" \
  -H "Authorization: Bearer your-jwt-token"
```

**Response:**
```json
{
  "success": true,
  "data": [/* array of task objects */],
  "message": "Today's tasks retrieved successfully",
  "meta": {
    "count": 5
  }
}
```

---

### 8. Get Overdue Tasks
Get all tasks that are past their due date and not completed.

**Endpoint:** `GET /tasks/overdue`

**Example Request:**
```bash
curl -X GET "http://localhost:8000/tasks/overdue" \
  -H "Authorization: Bearer your-jwt-token"
```

**Response:**
```json
{
  "success": true,
  "data": [/* array of task objects */],
  "message": "Overdue tasks retrieved successfully",
  "meta": {
    "count": 3
  }
}
```

---

### 9. Parse Natural Language
Parse natural language text into structured task data.

**Endpoint:** `POST /tasks/parse`

**Request Body:**
```json
{
  "text": "Remind me to call mom tomorrow at 3 PM #family"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/tasks/parse" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{"text": "High priority task to review budget by next week"}'
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "title": "review budget",
    "description": null,
    "due_date": "2025-07-01T10:00:00",
    "priority": "high",
    "tags": []
  },
  "message": "Text parsed successfully"
}
```

---

## Task Status Flow

Tasks can transition between statuses:
- `pending` → `in_progress`, `completed`, `cancelled`
- `in_progress` → `completed`, `cancelled`, `pending`
- `completed` → `pending` (to reopen)
- `cancelled` → `pending` (to reactivate)

When a task is marked as `completed`:
- `is_completed` is automatically set to `true`
- `completion_date` is set to current timestamp
- Optional `actual_duration` can be recorded

---

## Priority Levels

- `high`: Urgent and important tasks
- `medium`: Normal priority tasks (default)
- `low`: Tasks that can be done when time permits

Tasks are sorted by:
1. Due date (ascending, nulls last)
2. Priority (high → medium → low)
3. Creation date (newest first)

---

## Tags

Tags are stored as JSON arrays and can be used for:
- Categorization (e.g., "work", "personal", "health")
- Context (e.g., "home", "office", "travel")
- Projects (e.g., "website-redesign", "q2-planning")

---

## Error Responses

All endpoints return standard error responses:

**404 - Task Not Found:**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Task not found",
    "details": {}
  }
}
```

**400 - Validation Error:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "title",
      "issue": "Title cannot be empty"
    }
  }
}
```

**401 - Unauthorized:**
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required",
    "details": {}
  }
}
```
