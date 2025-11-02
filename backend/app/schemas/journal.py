from pydantic import BaseModel, field_validator, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from enum import Enum
import json


# Journal mood enum
class JournalMood(str, Enum):
    very_happy = "very_happy"
    happy = "happy"
    neutral = "neutral"
    sad = "sad"
    very_sad = "very_sad"
    angry = "angry"
    excited = "excited"
    anxious = "anxious"
    grateful = "grateful"


# Base journal entry schema
class JournalEntryBase(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    content: str = Field(..., min_length=1, max_length=10000)
    mood: Optional[JournalMood] = None
    weather: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=255)


class JournalEntryCreate(JournalEntryBase):
    pass


class JournalEntryUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = Field(None, min_length=1, max_length=10000)
    mood: Optional[JournalMood] = None
    weather: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=255)


class JournalEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    title: Optional[str]
    content: str
    mood: Optional[JournalMood]
    sentiment_score: Optional[float]
    keywords: Optional[List[str]]
    summary: Optional[str]
    weather: Optional[str]
    location: Optional[str]
    created_at: datetime
    updated_at: datetime

    @field_validator('keywords', mode='before')
    @classmethod
    def parse_keywords(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v else []
            except json.JSONDecodeError:
                return []
        return v or []


# Response schemas
class JournalEntryResponse(BaseModel):
    success: bool
    data: JournalEntryOut
    message: str
    meta: dict = {}


class JournalEntriesResponse(BaseModel):
    success: bool
    data: List[JournalEntryOut]
    message: str
    meta: dict


class MessageResponse(BaseModel):
    success: bool
    message: str
    meta: dict = {}


# Parse request schema
class JournalParseRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)


class JournalParseResponse(BaseModel):
    success: bool
    data: dict
    message: str
    meta: dict = {}


# Analysis schemas
class JournalAnalysisRequest(BaseModel):
    entry_ids: Optional[List[UUID]] = None  # If None, analyze all entries


class JournalStatsResponse(BaseModel):
    success: bool
    data: dict
    message: str
    meta: dict = {}


class MoodTrendsResponse(BaseModel):
    success: bool
    data: dict
    message: str
    meta: dict = {}
