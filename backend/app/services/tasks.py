from sqlalchemy.orm import Session
from sqlalchemy import and_, extract, func, desc, or_
from fastapi import HTTPException, status
from app.models.models import Task, User
from app.schemas.tasks import TaskCreate, TaskUpdate, TaskOut, TaskParseRequest, TaskPriority, TaskStatus
from typing import List, Optional
from datetime import datetime, date, timedelta
import json
from uuid import UUID


class TaskService:
    
    @staticmethod
    def get_tasks(
        db: Session, 
        user: User, 
        status_filter: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        due_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> dict:
        """Get tasks with filters and pagination"""
        query = db.query(Task).filter(Task.user_id == user.id)
        
        # Apply filters
        if status_filter:
            query = query.filter(Task.status == status_filter.value)
        if priority:
            query = query.filter(Task.priority == priority.value)
        if due_date:
            query = query.filter(func.date(Task.due_date) == due_date.date())
        if tags:
            # Filter tasks that have any of the specified tags
            tag_conditions = []
            for tag in tags:
                tag_conditions.append(Task.tags.like(f'%"{tag}"%'))
            query = query.filter(or_(*tag_conditions))
        if search:
            query = query.filter(
                or_(
                    Task.title.ilike(f"%{search}%"),
                    Task.description.ilike(f"%{search}%")
                )
            )
        
        # Count total for pagination
        total = query.count()
        
        # Apply pagination and ordering
        tasks = query.order_by(
            Task.due_date.asc().nullslast(),
            desc(Task.priority == 'high'),
            desc(Task.priority == 'medium'),
            Task.created_at.desc()
        ).offset((page - 1) * limit).limit(limit).all()
        
        # Convert to response format
        task_data = []
        for task in tasks:
            task_dict = {
                "id": task.id,
                "user_id": task.user_id,
                "title": task.title,
                "description": task.description,
                "due_date": task.due_date,
                "priority": task.priority,
                "status": task.status,
                "is_completed": task.is_completed,
                "completion_date": task.completion_date,
                "estimated_duration": task.estimated_duration,
                "actual_duration": task.actual_duration,
                "tags": TaskService._parse_tags(task.tags),
                "parent_task_id": task.parent_task_id,
                "created_at": task.created_at,
                "updated_at": task.updated_at
            }
            task_data.append(task_dict)
        
        return {
            "data": task_data,
            "meta": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    
    @staticmethod
    def create_task(db: Session, user: User, task_data: TaskCreate) -> dict:
        """Create a new task"""
        
        # If parent_task_id is provided, verify it exists and belongs to user
        if task_data.parent_task_id:
            parent_task = db.query(Task).filter(
                Task.id == task_data.parent_task_id,
                Task.user_id == user.id
            ).first()
            if not parent_task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent task not found"
                )
        
        # Create task
        db_task = Task(
            user_id=user.id,
            title=task_data.title,
            description=task_data.description,
            due_date=task_data.due_date,
            priority=task_data.priority.value,
            status=task_data.status.value,
            estimated_duration=task_data.estimated_duration,
            tags=json.dumps(task_data.tags) if task_data.tags else None,
            parent_task_id=task_data.parent_task_id
        )
        
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        
        return {
            "id": db_task.id,
            "user_id": db_task.user_id,
            "title": db_task.title,
            "description": db_task.description,
            "due_date": db_task.due_date,
            "priority": db_task.priority,
            "status": db_task.status,
            "is_completed": db_task.is_completed,
            "completion_date": db_task.completion_date,
            "estimated_duration": db_task.estimated_duration,
            "actual_duration": db_task.actual_duration,
            "tags": TaskService._parse_tags(db_task.tags),
            "parent_task_id": db_task.parent_task_id,
            "created_at": db_task.created_at,
            "updated_at": db_task.updated_at
        }
    
    @staticmethod
    def get_task_by_id(db: Session, user: User, task_id: UUID) -> dict:
        """Get a specific task by ID"""
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user.id
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        return {
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date,
            "priority": task.priority,
            "status": task.status,
            "is_completed": task.is_completed,
            "completion_date": task.completion_date,
            "estimated_duration": task.estimated_duration,
            "actual_duration": task.actual_duration,
            "tags": TaskService._parse_tags(task.tags),
            "parent_task_id": task.parent_task_id,
            "created_at": task.created_at,
            "updated_at": task.updated_at
        }
    
    @staticmethod
    def update_task(db: Session, user: User, task_id: UUID, task_data: TaskUpdate) -> dict:
        """Update an existing task"""
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user.id
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # If parent_task_id is provided, verify it exists and belongs to user
        if task_data.parent_task_id:
            parent_task = db.query(Task).filter(
                Task.id == task_data.parent_task_id,
                Task.user_id == user.id
            ).first()
            if not parent_task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent task not found"
                )
        
        # Update fields that are provided
        update_data = task_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == 'tags' and value is not None:
                setattr(task, field, json.dumps(value))
            elif field in ['priority', 'status'] and value is not None:
                setattr(task, field, value.value)
            elif value is not None:
                setattr(task, field, value)
        
        # Auto-update completion status based on task status
        if hasattr(task_data, 'status') and task_data.status:
            if task_data.status == TaskStatus.completed:
                task.is_completed = True
                if not task.completion_date:
                    task.completion_date = datetime.utcnow()
            else:
                task.is_completed = False
                task.completion_date = None
        
        db.commit()
        db.refresh(task)
        
        return {
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date,
            "priority": task.priority,
            "status": task.status,
            "is_completed": task.is_completed,
            "completion_date": task.completion_date,
            "estimated_duration": task.estimated_duration,
            "actual_duration": task.actual_duration,
            "tags": TaskService._parse_tags(task.tags),
            "parent_task_id": task.parent_task_id,
            "created_at": task.created_at,
            "updated_at": task.updated_at
        }
    
    @staticmethod
    def delete_task(db: Session, user: User, task_id: UUID) -> bool:
        """Delete a task"""
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user.id
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Also delete any subtasks
        db.query(Task).filter(Task.parent_task_id == task_id).delete()
        
        db.delete(task)
        db.commit()
        
        return True
    
    @staticmethod
    def complete_task(db: Session, user: User, task_id: UUID, actual_duration: Optional[int] = None) -> dict:
        """Mark a task as completed"""
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user.id
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        task.status = TaskStatus.completed.value
        task.is_completed = True
        task.completion_date = datetime.utcnow()
        
        if actual_duration:
            task.actual_duration = actual_duration
        
        db.commit()
        db.refresh(task)
        
        return {
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date,
            "priority": task.priority,
            "status": task.status,
            "is_completed": task.is_completed,
            "completion_date": task.completion_date,
            "estimated_duration": task.estimated_duration,
            "actual_duration": task.actual_duration,
            "tags": TaskService._parse_tags(task.tags),
            "parent_task_id": task.parent_task_id,
            "created_at": task.created_at,
            "updated_at": task.updated_at
        }
    
    @staticmethod
    def _parse_tags(tags):
        """Helper method to safely parse tags field"""
        if not tags:
            return []
        if isinstance(tags, list):
            return tags
        if isinstance(tags, str):
            try:
                return json.loads(tags)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    @staticmethod
    def get_today_tasks(db: Session, user: User) -> List[dict]:
        """Get tasks due today"""
        today = datetime.now().date()
        tasks = db.query(Task).filter(
            Task.user_id == user.id,
            func.date(Task.due_date) == today,
            Task.status != TaskStatus.completed.value
        ).order_by(
            desc(Task.priority == 'high'),
            desc(Task.priority == 'medium'),
            Task.created_at.desc()
        ).all()
        
        return [{
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date,
            "priority": task.priority,
            "status": task.status,
            "is_completed": task.is_completed,
            "completion_date": task.completion_date,
            "estimated_duration": task.estimated_duration,
            "actual_duration": task.actual_duration,
            "tags": TaskService._parse_tags(task.tags),
            "parent_task_id": task.parent_task_id,
            "created_at": task.created_at,
            "updated_at": task.updated_at
        } for task in tasks]
    
    @staticmethod
    def get_overdue_tasks(db: Session, user: User) -> List[dict]:
        """Get overdue tasks"""
        now = datetime.now()
        tasks = db.query(Task).filter(
            Task.user_id == user.id,
            Task.due_date < now,
            Task.status != TaskStatus.completed.value
        ).order_by(Task.due_date.asc()).all()
        
        return [{
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date,
            "priority": task.priority,
            "status": task.status,
            "is_completed": task.is_completed,
            "completion_date": task.completion_date,
            "estimated_duration": task.estimated_duration,
            "actual_duration": task.actual_duration,
            "tags": TaskService._parse_tags(task.tags),
            "parent_task_id": task.parent_task_id,
            "created_at": task.created_at,
            "updated_at": task.updated_at
        } for task in tasks]
    
    @staticmethod
    def parse_natural_language(text: str) -> dict:
        """Parse natural language text into task data"""
        # This is a simplified implementation
        # In a real application, you would integrate with Google Gemini or another NLU service
        
        result = {
            "title": "",
            "description": None,
            "due_date": None,
            "priority": "medium",
            "tags": []
        }
        
        # Simple keyword-based parsing
        text_lower = text.lower()
        
        # Extract title (first part before any time indicators)
        title_indicators = ["by", "on", "before", "at", "due", "tomorrow", "today", "next"]
        title_parts = text.split()
        title_end = len(title_parts)
        
        for i, word in enumerate(title_parts):
            if word.lower() in title_indicators:
                title_end = i
                break
        
        result["title"] = " ".join(title_parts[:title_end]).strip()
        
        # Extract priority
        if any(word in text_lower for word in ["urgent", "important", "asap", "high priority"]):
            result["priority"] = "high"
        elif any(word in text_lower for word in ["low priority", "when possible", "sometime"]):
            result["priority"] = "low"
        
        # Extract basic time references
        if "tomorrow" in text_lower:
            from datetime import datetime, timedelta
            result["due_date"] = (datetime.now() + timedelta(days=1)).isoformat()
        elif "today" in text_lower:
            result["due_date"] = datetime.now().isoformat()
        elif "next week" in text_lower:
            result["due_date"] = (datetime.now() + timedelta(weeks=1)).isoformat()
        
        # Extract tags
        if "#" in text:
            import re
            tags = re.findall(r'#(\w+)', text)
            result["tags"] = tags
        
        return result

    @staticmethod
    async def parse_text_with_ai(db: Session, user: User, text: str) -> dict:
        """Parse task from natural language text using AI"""
        from app.services.ai_service import ai_service
        try:
            parsed_data = await ai_service.parse_text_task(text)
            if not parsed_data.get('is_task_related', True):
                return {
                    "success": False,
                    "data": None,
                    "parsed_data": None,
                    "confidence": 0,
                    "message": parsed_data.get('message', 'Please provide a valid task description. For example: "Finish the project report by Friday" or "Call the bank tomorrow".')
                }
            if parsed_data.get('confidence', 0) < 0.5:
                return {
                    "success": False,
                    "data": None,
                    "parsed_data": parsed_data,
                    "confidence": parsed_data.get('confidence', 0),
                    "message": "Low confidence in parsing. Please provide more details about your task (title, due date, etc.)."
                }
            # Create task from parsed data
            task_create = TaskCreate(
                title=parsed_data['title'],
                description=parsed_data.get('description'),
                due_date=datetime.fromisoformat(parsed_data['due_date']) if parsed_data.get('due_date') else None,
                priority=TaskPriority(parsed_data.get('priority', 'medium')),
                status=TaskStatus(parsed_data.get('status', 'pending')),
                tags=parsed_data.get('tags', [])
            )
            result = TaskService.create_task(db, user, task_create)
            return {
                "success": True,
                "data": result,
                "parsed_data": parsed_data,
                "confidence": parsed_data.get('confidence', 0.8),
                "message": "Task created successfully from text"
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "parsed_data": None,
                "confidence": 0,
                "message": f"Error parsing text: {str(e)}"
            }

    @staticmethod
    async def parse_voice_with_ai(db: Session, user: User, audio_file) -> dict:
        """Parse task from voice recording using AI"""
        from app.services.ai_service import ai_service
        try:
            parsed_data = await ai_service.parse_voice_task(audio_file)
            if parsed_data.get('confidence', 0) < 0.5:
                return {
                    "success": False,
                    "data": None,
                    "parsed_data": parsed_data,
                    "confidence": parsed_data.get('confidence', 0),
                    "transcribed_text": parsed_data.get('transcribed_text'),
                    "message": "Low confidence in voice parsing. Please speak more clearly."
                }
            task_create = TaskCreate(
                title=parsed_data['title'],
                description=parsed_data.get('description'),
                due_date=datetime.fromisoformat(parsed_data['due_date']) if parsed_data.get('due_date') else None,
                priority=TaskPriority(parsed_data.get('priority', 'medium')),
                status=TaskStatus(parsed_data.get('status', 'pending')),
                tags=parsed_data.get('tags', [])
            )
            result = TaskService.create_task(db, user, task_create)
            return {
                "success": True,
                "data": result,
                "parsed_data": parsed_data,
                "confidence": parsed_data.get('confidence', 0.8),
                "transcribed_text": parsed_data.get('transcribed_text'),
                "message": "Task created successfully from voice"
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "parsed_data": None,
                "confidence": 0,
                "transcribed_text": None,
                "message": f"Error parsing voice: {str(e)}"
            }
