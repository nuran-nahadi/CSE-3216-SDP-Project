from fastapi import APIRouter, Depends, Query, Path, status, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from app.core.dependencies import get_database_session
from app.core.dependencies import get_current_user
from app.decorators import rate_limit
from app.services.events import EventService
from app.schemas.events import (
    EventCreate, EventUpdate, EventParseRequest,
    EventResponse, EventsResponse, CalendarResponse, 
    MessageResponse, EventParseResponse, AIEventParseRequest, AIEventParseResponse
)
from app.models.models import User
from typing import Optional, List
from datetime import datetime
from uuid import UUID


router = APIRouter(tags=["Events"], prefix="/events")


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=EventsResponse,
    summary="List events",
    description="Retrieve events with optional filters and pagination"
)
def get_events(
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    search: Optional[str] = Query(None, description="Search in title, description, location"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """List events with filters"""
    result = EventService.get_events(
        db, current_user, start_date, end_date, tags, search, page, limit
    )
    return {
        "success": True,
        "data": result["data"],
        "message": "Events retrieved successfully",
        "meta": result["meta"]
    }


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=EventResponse,
    summary="Create new event",
    description="Create a new event"
)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Create a new event"""
    result = EventService.create_event(db, current_user, event)
    return {
        "success": True,
        "data": result["data"],
        "message": "Event created successfully",
        "meta": {"timestamp": datetime.utcnow()}
    }


@router.get(
    "/{event_id}",
    status_code=status.HTTP_200_OK,
    response_model=EventResponse,
    summary="Get specific event",
    description="Retrieve a specific event by ID"
)
def get_event(
    event_id: UUID,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Get a specific event by ID"""
    result = EventService.get_event_by_id(db, current_user, event_id)
    return {
        "success": True,
        "data": result["data"],
        "message": "Event retrieved successfully",
        "meta": {"timestamp": datetime.utcnow()}
    }


@router.put(
    "/{event_id}",
    status_code=status.HTTP_200_OK,
    response_model=EventResponse,
    summary="Update event",
    description="Update an existing event"
)
def update_event(
    event_id: UUID,
    event: EventUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Update an existing event"""
    result = EventService.update_event(db, current_user, event_id, event)
    return {
        "success": True,
        "data": result["data"],
        "message": "Event updated successfully",
        "meta": {"timestamp": datetime.utcnow()}
    }


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse,
    summary="Delete event",
    description="Delete an existing event"
)
def delete_event(
    event_id: UUID,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Delete an existing event"""
    EventService.delete_event(db, current_user, event_id)
    return {
        "success": True,
        "message": "Event deleted successfully",
        "meta": {"timestamp": datetime.utcnow()}
    }


@router.get(
    "/calendar/{year}/{month}",
    status_code=status.HTTP_200_OK,
    response_model=CalendarResponse,
    summary="Get calendar view",
    description="Get calendar view for a specific month"
)
def get_calendar_view(
    year: int = Path(..., ge=1900, le=3000, description="Year"),
    month: int = Path(..., ge=1, le=12, description="Month"),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Get calendar view for a specific month"""
    result = EventService.get_calendar_view(db, current_user, year, month)
    return {
        "success": True,
        "data": result["data"],
        "message": "Calendar view retrieved successfully",
        "meta": {"timestamp": datetime.utcnow()}
    }


@router.get(
    "/upcoming",
    status_code=status.HTTP_200_OK,
    response_model=EventsResponse,
    summary="Get upcoming events",
    description="Get upcoming events for the next 7 days"
)
def get_upcoming_events(
    days: int = Query(7, ge=1, le=30, description="Number of days to look ahead"),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Get upcoming events for the next N days"""
    result = EventService.get_upcoming_events(db, current_user, days)
    return {
        "success": True,
        "data": result["data"],
        "message": "Upcoming events retrieved successfully",
        "meta": result["meta"]
    }


@router.post(
    "/parse",
    status_code=status.HTTP_200_OK,
    response_model=EventParseResponse,
    summary="Parse natural language",
    description="Parse natural language into event data"
)
def parse_natural_language(
    request: EventParseRequest,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Parse natural language text into event data"""
    result = EventService.parse_natural_language(request.text)
    return {
        "success": True,
        "data": result["data"],
        "message": "Text parsed successfully",
        "meta": {"timestamp": datetime.utcnow()}
    }


@router.post(
    "/ai/parse-text",
    status_code=status.HTTP_201_CREATED,
    response_model=AIEventParseResponse,
    summary="Parse event from text using AI",
    description="Parse natural language text into event data using Gemini AI"
)
@rate_limit(limit=30, window=60)
async def parse_text_with_ai(
    request: AIEventParseRequest,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Parse event from natural language text using AI"""
    return await EventService.parse_text_with_ai(db, current_user, request.text)

@router.post(
    "/ai/parse-voice",
    status_code=status.HTTP_201_CREATED,
    response_model=AIEventParseResponse,
    summary="Parse event from voice using AI",
    description="Parse voice recording into event data using Gemini AI"
)
@rate_limit(limit=10, window=300)
async def parse_voice_with_ai(
    file: UploadFile = File(..., description="Audio file (MP3, WAV, M4A, etc.)"),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Parse event from voice using AI"""
    allowed_audio_types = ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/m4a', 'audio/x-m4a']
    if not file.content_type or file.content_type not in allowed_audio_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an audio file (MP3, WAV, M4A)"
        )
    return await EventService.parse_voice_with_ai(db, current_user, file)
