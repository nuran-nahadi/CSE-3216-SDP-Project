from pydantic import BaseModel, field_validator, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID
import json


class BaseConfig:
    from_attributes = True


# Base event schema
class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    tags: Optional[List[str]] = None
    is_all_day: bool = False
    reminder_minutes: Optional[int] = Field(None, ge=0)
    recurrence_rule: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')

    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v else []
            except json.JSONDecodeError:
                return []
        return v or []

    @field_validator('end_time')
    @classmethod
    def validate_end_time(cls, v, info):
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('End time must be after start time')
        return v


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    tags: Optional[List[str]] = None
    is_all_day: Optional[bool] = None
    reminder_minutes: Optional[int] = Field(None, ge=0)
    recurrence_rule: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')

    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v else []
            except json.JSONDecodeError:
                return []
        return v or []

    @field_validator('end_time')
    @classmethod
    def validate_end_time(cls, v, info):
        if v is not None and 'start_time' in info.data and info.data['start_time'] is not None:
            if v <= info.data['start_time']:
                raise ValueError('End time must be after start time')
        return v


class EventOut(EventBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config(BaseConfig):
        pass


class EventParseRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Natural language text to parse into event data")


class EventParsed(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    tags: Optional[List[str]] = None
    is_all_day: Optional[bool] = False
    confidence_score: float = Field(..., ge=0.0, le=1.0)


# Response models
class EventResponse(BaseModel):
    success: bool = True
    data: EventOut
    message: str = "Event retrieved successfully"
    meta: dict = {}

    class Config(BaseConfig):
        pass


class EventsResponse(BaseModel):
    success: bool = True
    data: List[EventOut]
    message: str = "Events retrieved successfully"
    meta: dict = {}

    class Config(BaseConfig):
        pass


class MessageResponse(BaseModel):
    success: bool = True
    message: str
    meta: dict = {}


class CalendarResponse(BaseModel):
    success: bool = True
    data: dict  # Contains calendar structure with events
    message: str = "Calendar view retrieved successfully"
    meta: dict = {}

    class Config(BaseConfig):
        pass


class EventParseResponse(BaseModel):
    success: bool = True
    data: EventParsed
    message: str = "Text parsed successfully"
    meta: dict = {}

    class Config(BaseConfig):
        pass


class AIEventParseRequest(BaseModel):
    """Schema for AI event parsing from text"""
    text: str
    class Config(BaseConfig):
        pass

class AIEventParseResponse(BaseModel):
    """Response schema for AI-parsed event"""
    success: bool = True
    data: Optional[EventOut] = None
    parsed_data: Optional[dict] = None
    confidence: Optional[float] = None
    transcribed_text: Optional[str] = None  # For voice inputs
    message: str = "Text parsed successfully"
    class Config(BaseConfig):
        pass
