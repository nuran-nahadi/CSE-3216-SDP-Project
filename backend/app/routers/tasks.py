from fastapi import APIRouter, Depends, Query, Path, status, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from app.core.dependencies import get_database_session
from app.core.dependencies import get_current_user
from app.decorators import rate_limit
from app.services.tasks import TaskService
from app.schemas.tasks import (
    TaskCreate, TaskUpdate, TaskParseRequest, TaskCompleteRequest,
    TaskResponse, TasksResponse, MessageResponse, TaskParseResponse,
    TaskPriority, TaskStatus, AITaskParseRequest, AITaskParseResponse, TaskStatsResponse
)
from app.models.models import User, Task
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.services.ai_service import ai_service


router = APIRouter(tags=["Tasks"], prefix="/tasks")


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=TasksResponse,
    summary="List tasks",
    description="Retrieve tasks with optional filters and pagination"
)
def get_tasks(
    status_filter: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    due_date: Optional[datetime] = Query(None, description="Filter by due date"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """List tasks with filters"""
    result = TaskService.get_tasks(
        db, current_user, status_filter, priority, due_date, tags, search, page, limit
    )
    return {
        "success": True,
        "data": result["data"],
        "message": "Tasks retrieved successfully",
        "meta": result["meta"]
    }


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskResponse,
    summary="Create task",
    description="Create a new task"
)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Create a new task"""
    task = TaskService.create_task(db, current_user, task_data)
    return {
        "success": True,
        "data": task,
        "message": "Task created successfully"
    }


@router.get(
    "/today",
    status_code=status.HTTP_200_OK,
    response_model=TasksResponse,
    summary="Get today's tasks",
    description="Get tasks due today"
)
def get_today_tasks(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Get today's tasks"""
    tasks = TaskService.get_today_tasks(db, current_user)
    return {
        "success": True,
        "data": tasks,
        "message": "Today's tasks retrieved successfully",
        "meta": {"count": len(tasks)}
    }


@router.get(
    "/overdue",
    status_code=status.HTTP_200_OK,
    response_model=TasksResponse,
    summary="Get overdue tasks",
    description="Get overdue tasks"
)
def get_overdue_tasks(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Get overdue tasks"""
    tasks = TaskService.get_overdue_tasks(db, current_user)
    return {
        "success": True,
        "data": tasks,
        "message": "Overdue tasks retrieved successfully",
        "meta": {"count": len(tasks)}
    }


@router.get(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=TaskResponse,
    summary="Get task",
    description="Get a specific task by ID"
)
def get_task(
    task_id: UUID = Path(..., description="Task ID"),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Get a specific task"""
    task = TaskService.get_task_by_id(db, current_user, task_id)
    return {
        "success": True,
        "data": task,
        "message": "Task retrieved successfully"
    }


@router.put(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=TaskResponse,
    summary="Update task",
    description="Update an existing task"
)
def update_task(
    task_data: TaskUpdate,
    task_id: UUID = Path(..., description="Task ID"),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Update an existing task"""
    task = TaskService.update_task(db, current_user, task_id, task_data)
    return {
        "success": True,
        "data": task,
        "message": "Task updated successfully"
    }


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse,
    summary="Delete task",
    description="Delete a task"
)
def delete_task(
    task_id: UUID = Path(..., description="Task ID"),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Delete a task"""
    TaskService.delete_task(db, current_user, task_id)
    return {
        "success": True,
        "message": "Task deleted successfully"
    }


@router.patch(
    "/{task_id}/complete",
    status_code=status.HTTP_200_OK,
    response_model=TaskResponse,
    summary="Complete task",
    description="Mark a task as completed"
)
def complete_task(
    complete_data: TaskCompleteRequest,
    task_id: UUID = Path(..., description="Task ID"),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Mark a task as completed"""
    task = TaskService.complete_task(db, current_user, task_id, complete_data.actual_duration)
    return {
        "success": True,
        "data": task,
        "message": "Task marked as completed"
    }


@router.post(
    "/parse",
    status_code=status.HTTP_200_OK,
    response_model=TaskParseResponse,
    summary="Parse natural language",
    description="Parse natural language text into task data"
)
def parse_task_text(
    parse_data: TaskParseRequest,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Parse natural language text into task data"""
    parsed_data = TaskService.parse_natural_language(parse_data.text)
    return {
        "success": True,
        "data": parsed_data,
        "message": "Text parsed successfully"
    }

# AI-powered endpoints
@router.post(
    "/ai/parse-text",
    status_code=status.HTTP_201_CREATED,
    response_model=AITaskParseResponse,
    summary="Parse task from text using AI",
    description="Parse natural language text into task data using Gemini AI"
)
@rate_limit(limit=30, window=60)
async def parse_text_with_ai(
    request: AITaskParseRequest,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Parse task from natural language text using AI"""
    return await TaskService.parse_text_with_ai(db, current_user, request.text)

@router.post(
    "/ai/parse-voice",
    status_code=status.HTTP_201_CREATED,
    response_model=AITaskParseResponse,
    summary="Parse task from voice using AI",
    description="Parse voice recording into task data using Gemini AI"
)
@rate_limit(limit=10, window=300)
async def parse_voice_with_ai(
    file: UploadFile = File(..., description="Audio file (MP3, WAV, M4A, etc.)"),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Parse task from voice using AI"""
    allowed_audio_types = ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/m4a', 'audio/x-m4a']
    if not file.content_type or file.content_type not in allowed_audio_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an audio file (MP3, WAV, M4A)"
        )
    return await TaskService.parse_voice_with_ai(db, current_user, file)


@router.get(
    "/ai/insights",
    status_code=status.HTTP_200_OK,
    response_model=TaskStatsResponse,
    summary="AI Task Insights",
    description="Generate AI-powered insights and recommendations for the user's tasks"
)
@rate_limit(limit=20, window=300)
async def get_task_ai_insights(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Generate AI-powered insights and recommendations for the user's tasks"""
    # Fetch all tasks for the user
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    if not tasks:
        return {
            "success": True,
            "data": {},
            "message": "No tasks found for insights.",
            "meta": {}
        }

    # Prepare stats for the prompt
    from collections import defaultdict
    from datetime import datetime, timedelta
    import json

    now = datetime.now()
    week_start = now - timedelta(days=now.weekday())
    week_end = week_start + timedelta(days=6)
    today = now.date()

    stats = {
        "total_tasks": len(tasks),
        "completed_tasks": 0,
        "failed_tasks": 0,
        "pending_tasks": 0,
        "in_progress_tasks": 0,
        "cancelled_tasks": 0,
        "completed_today": 0,
        "failed_today": 0,
        "completed_this_week": 0,
        "failed_this_week": 0,
        "high_priority_missed_this_week": [],
        "recurring_missed": [],
        "recurring_completed": [],
        "recurring_total": 0,
        "tasks_per_day": defaultdict(int),
        "completed_per_day": defaultdict(int),
        "failed_per_day": defaultdict(int),
    }

    for task in tasks:
        due = task.due_date.date() if task.due_date else None
        completed = task.completion_date.date() if task.completion_date else None
        is_recurring = bool(task.recurrence_rule) if hasattr(task, 'recurrence_rule') else False
        # Status counts
        if task.status == "completed":
            stats["completed_tasks"] += 1
            if completed == today:
                stats["completed_today"] += 1
            if completed and week_start.date() <= completed <= week_end.date():
                stats["completed_this_week"] += 1
            if due:
                stats["completed_per_day"][str(due)] += 1
            if is_recurring:
                stats["recurring_completed"].append(task.title)
        elif task.status == "cancelled":
            stats["cancelled_tasks"] += 1
        elif task.status == "in_progress":
            stats["in_progress_tasks"] += 1
        else:
            stats["pending_tasks"] += 1
            if due == today and (not task.is_completed):
                stats["failed_today"] += 1
            if due and week_start.date() <= due <= week_end.date() and (not task.is_completed):
                stats["failed_this_week"] += 1
            if due:
                stats["failed_per_day"][str(due)] += 1
        # Per day
        if due:
            stats["tasks_per_day"][str(due)] += 1
        # Missed high priority this week
        if (
            task.priority == "high"
            and due and week_start.date() <= due <= week_end.date()
            and not task.is_completed
        ):
            stats["high_priority_missed_this_week"].append(task.title)
        # Recurring missed
        if is_recurring:
            stats["recurring_total"] += 1
            if not task.is_completed and due and due < now.date():
                stats["recurring_missed"].append(task.title)

    # Convert defaultdicts to dicts
    stats["tasks_per_day"] = dict(stats["tasks_per_day"])
    stats["completed_per_day"] = dict(stats["completed_per_day"])
    stats["failed_per_day"] = dict(stats["failed_per_day"])


    prompt = f'''
You are an expert productivity and task management assistant. Analyze the following user's task data and provide actionable insights and recommendations in JSON format.

User's task statistics:
{json.dumps(stats, indent=2)}

Definitions:
- "failed" means a task was due but not completed by its due date.
- "recurring_missed" are recurring tasks that were not completed on time.
- "high_priority_missed_this_week" are high priority tasks due this week but not completed.

Please provide insights in this JSON format:
{{
  "summary": "A brief summary of the user's task performance.",
  "insights": [
    "Insight 1",
    "Insight 2",
    "..."
  ],
  "recommendations": [
    "Recommendation 1",
    "Recommendation 2",
    "..."
  ],
  "missed_high_priority_tasks": [
    "Task title 1",
    "Task title 2"
  ],
  "missed_recurring_tasks": [
    "Task title 1",
    "Task title 2"
  ],
}}

Focus on:
- Patterns in completion and failure rates per day and week
- Missed high priority and recurring tasks
- Suggestions for improving productivity and task completion
- Any anomalies or trends (e.g., always missing tasks on certain days)
- Encourage positive habits and address recurring failures

Return only a valid JSON object as specified above.
'''

    # Call Gemini for insights
    ai_response = await ai_service.model.generate_content_async(prompt)
    # Extract JSON from response
    from app.services.ai_service import GeminiAIService
    result = GeminiAIService._extract_json_from_response(GeminiAIService, ai_response.text, task=False)
    if not result:
        print("Gemini AI raw response:", ai_response.text)
        return {
            "success": False,
            "data": {},
            "message": "Failed to generate AI insights.",
            "meta": {}
        }
    return {
        "success": True,
        "data": result,
        "message": "AI task insights generated successfully.",
        "meta": {}
    }