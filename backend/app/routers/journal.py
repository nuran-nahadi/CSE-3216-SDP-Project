from fastapi import APIRouter, Depends, Query, Path, status, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_database_session
from app.core.dependencies import get_current_user
from app.services.journal import JournalService
from app.schemas.journal import (
    JournalEntryCreate, JournalEntryUpdate, JournalParseRequest,
    JournalEntryResponse, JournalEntriesResponse, MessageResponse, 
    JournalParseResponse, JournalAnalysisRequest, JournalStatsResponse,
    MoodTrendsResponse
)
from app.models.models import User
from typing import Optional, List
from datetime import datetime
from uuid import UUID


router = APIRouter(tags=["Journal"], prefix="/journal")


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=JournalEntriesResponse,
    summary="List journal entries",
    description="Retrieve journal entries with optional filters and pagination"
)
def get_journal_entries(
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    mood: Optional[str] = Query(None, description="Filter by mood"),
    search: Optional[str] = Query(None, description="Search in title, content, summary"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """List journal entries with filters"""
    result = JournalService.get_entries(
        db, current_user, start_date, end_date, mood, search, page, limit
    )
    return {
        "success": True,
        "data": result["data"],
        "message": "Journal entries retrieved successfully",
        "meta": result["meta"]
    }


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=JournalEntryResponse,
    summary="Create journal entry",
    description="Create a new journal entry with AI analysis"
)
def create_journal_entry(
    entry_data: JournalEntryCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Create a new journal entry"""
    entry = JournalService.create_entry(db, current_user, entry_data)
    return {
        "success": True,
        "data": entry,
        "message": "Journal entry created successfully",
        "meta": {"timestamp": datetime.now().isoformat()}
    }


@router.get(
    "/{entry_id}",
    status_code=status.HTTP_200_OK,
    response_model=JournalEntryResponse,
    summary="Get journal entry",
    description="Retrieve a specific journal entry by ID"
)
def get_journal_entry(
    entry_id: UUID = Path(..., description="Journal entry ID"),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Get a specific journal entry"""
    entry = JournalService.get_entry_by_id(db, current_user, entry_id)
    return {
        "success": True,
        "data": entry,
        "message": "Journal entry retrieved successfully",
        "meta": {"timestamp": datetime.now().isoformat()}
    }


@router.put(
    "/{entry_id}",
    status_code=status.HTTP_200_OK,
    response_model=JournalEntryResponse,
    summary="Update journal entry",
    description="Update a journal entry"
)
def update_journal_entry(
    entry_id: UUID = Path(..., description="Journal entry ID"),
    entry_data: JournalEntryUpdate = ...,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Update a journal entry"""
    entry = JournalService.update_entry(db, current_user, entry_id, entry_data)
    return {
        "success": True,
        "data": entry,
        "message": "Journal entry updated successfully",
        "meta": {"timestamp": datetime.now().isoformat()}
    }


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse,
    summary="Delete journal entry",
    description="Delete a journal entry"
)
def delete_journal_entry(
    entry_id: UUID = Path(..., description="Journal entry ID"),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Delete a journal entry"""
    JournalService.delete_entry(db, current_user, entry_id)
    return {
        "success": True,
        "message": "Journal entry deleted successfully",
        "meta": {"timestamp": datetime.now().isoformat()}
    }


@router.post(
    "/analyze",
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse,
    summary="Trigger AI analysis",
    description="Trigger AI analysis for existing journal entries"
)
def analyze_journal_entries(
    analysis_request: JournalAnalysisRequest,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Trigger AI analysis for journal entries"""
    result = JournalService.analyze_entries(db, current_user, analysis_request.entry_ids)
    return {
        "success": True,
        "message": result["message"],
        "meta": {
            "analyzed_entries": result["analyzed_entries"],
            "timestamp": datetime.now().isoformat()
        }
    }


@router.get(
    "/stats",
    status_code=status.HTTP_200_OK,
    response_model=JournalStatsResponse,
    summary="Get journaling statistics",
    description="Get journaling statistics and metrics"
)
def get_journal_stats(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Get journaling statistics"""
    stats = JournalService.get_journal_stats(db, current_user)
    return {
        "success": True,
        "data": stats,
        "message": "Journal statistics retrieved successfully",
        "meta": {"timestamp": datetime.now().isoformat()}
    }


@router.post(
    "/parse",
    status_code=status.HTTP_200_OK,
    response_model=JournalParseResponse,
    summary="Parse natural language",
    description="Parse natural language input into journal entry data"
)
def parse_journal_text(
    parse_request: JournalParseRequest,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Parse natural language into journal data"""
    parsed_data = JournalService.parse_natural_language(parse_request.text)
    return {
        "success": True,
        "data": parsed_data,
        "message": "Text parsed successfully",
        "meta": {"timestamp": datetime.now().isoformat()}
    }


@router.get(
    "/mood-trends",
    status_code=status.HTTP_200_OK,
    response_model=MoodTrendsResponse,
    summary="Get mood trends",
    description="Get mood trends over time"
)
def get_mood_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Get mood trends over time"""
    trends = JournalService.get_mood_trends(db, current_user, days)
    return {
        "success": True,
        "data": trends,
        "message": "Mood trends retrieved successfully",
        "meta": {"timestamp": datetime.now().isoformat()}
    }
