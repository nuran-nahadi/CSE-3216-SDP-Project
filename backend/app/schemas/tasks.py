from pydantic import BaseModel, field_validator, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID
import json
from enum import Enum


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


# Base task schema
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.medium
    status: TaskStatus = TaskStatus.pending
    estimated_duration: Optional[int] = Field(None, ge=1, description="Estimated duration in minutes")
    tags: Optional[List[str]] = None
    parent_task_id: Optional[UUID] = None

    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v else []
            except json.JSONDecodeError:
                return []
        return v or []


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    estimated_duration: Optional[int] = Field(None, ge=1, description="Estimated duration in minutes")
    actual_duration: Optional[int] = Field(None, ge=1, description="Actual duration in minutes")
    tags: Optional[List[str]] = None
    parent_task_id: Optional[UUID] = None

    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v else []
            except json.JSONDecodeError:
                return []
        return v or []


class TaskOut(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    due_date: Optional[datetime]
    priority: TaskPriority
    status: TaskStatus
    is_completed: bool
    completion_date: Optional[datetime]
    estimated_duration: Optional[int]
    actual_duration: Optional[int]
    tags: Optional[List[str]]
    parent_task_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v else []
            except json.JSONDecodeError:
                return []
        return v or []


class TaskCompleteRequest(BaseModel):
    actual_duration: Optional[int] = Field(None, ge=1, description="Actual duration in minutes")


class TaskParseRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Natural language text to parse")


# Response schemas
class TaskResponse(BaseModel):
    success: bool = True
    data: TaskOut
    message: str = "Operation completed successfully"
    meta: dict = {}


class TasksResponse(BaseModel):
    success: bool = True
    data: List[TaskOut]
    message: str = "Tasks retrieved successfully"
    meta: dict = {}


class MessageResponse(BaseModel):
    success: bool = True
    message: str
    meta: dict = {}


class TaskParseResponse(BaseModel):
    success: bool = True
    data: dict
    message: str = "Text parsed successfully"
    meta: dict = {}


class TaskStatsResponse(BaseModel):
    success: bool = True
    data: dict
    message: str = "Task statistics retrieved successfully"
    meta: dict = {}


# AI parsing schemas
class AITaskParseRequest(BaseModel):
    """Schema for AI task parsing from text"""
    text: str
    
    class Config:
        from_attributes = True


class AITaskParseResponse(BaseModel):
    """Response schema for AI-parsed task"""
    success: bool = True
    data: Optional[TaskOut] = None
    parsed_data: Optional[dict] = None
    confidence: Optional[float] = None
    transcribed_text: Optional[str] = None  # For voice inputs
    message: str = "Text parsed successfully"
    
    class Config:
        from_attributes = True


class AITaskInsightsResponse(BaseModel):
    """Response schema for AI-generated task insights"""
    success: bool = True
    data: dict
    message: str = "Task insights retrieved successfully"
    
    class Config:
        from_attributes = True
