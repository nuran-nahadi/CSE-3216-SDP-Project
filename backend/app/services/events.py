from sqlalchemy.orm import Session
from sqlalchemy import and_, extract, func, desc, or_
from fastapi import HTTPException, status
from app.models.models import Event, User
from app.schemas.events import EventCreate, EventUpdate, EventOut, EventParseRequest
from typing import List, Optional
from datetime import datetime, date, timedelta
import json
from uuid import UUID
import calendar
from app.services.ai_service import ai_service
from app.schemas.events import AIEventParseResponse, AIEventParseRequest, AIEventParseResponse, EventCreate, EventOut


class EventService:
    
    @staticmethod
    def get_events(
        db: Session, 
        user: User, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> dict:
        """Get events with filters and pagination"""
        query = db.query(Event).filter(Event.user_id == user.id)
        
        # Apply filters
        if start_date:
            query = query.filter(Event.start_time >= start_date)
        if end_date:
            query = query.filter(Event.end_time <= end_date)
        if tags:
            # Filter events that have any of the specified tags
            tag_conditions = []
            for tag in tags:
                tag_conditions.append(Event.tags.like(f'%"{tag}"%'))
            query = query.filter(or_(*tag_conditions))
        if search:
            query = query.filter(
                or_(
                    Event.title.ilike(f"%{search}%"),
                    Event.description.ilike(f"%{search}%"),
                    Event.location.ilike(f"%{search}%")
                )
            )
        
        # Order by start time
        query = query.order_by(Event.start_time)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        events = query.offset(offset).limit(limit).all()
        
        # Convert to response format
        event_data = []
        for event in events:
            event_dict = {
                "id": event.id,
                "user_id": event.user_id,
                "title": event.title,
                "description": event.description,
                "start_time": event.start_time,
                "end_time": event.end_time,
                "location": event.location,
                "tags": json.loads(event.tags) if event.tags else [],
                "is_all_day": event.is_all_day,
                "reminder_minutes": event.reminder_minutes,
                "recurrence_rule": event.recurrence_rule,
                "color": event.color,
                "created_at": event.created_at,
                "updated_at": event.updated_at
            }
            event_data.append(event_dict)
        
        return {
            "data": event_data,
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit,
                "timestamp": datetime.utcnow()
            }
        }

    @staticmethod
    def create_event(db: Session, user: User, event_data: EventCreate) -> dict:
        """Create a new event"""
        try:
            # Convert tags to JSON string if provided
            tags_json = json.dumps(event_data.tags) if event_data.tags else None
            
            new_event = Event(
                user_id=user.id,
                title=event_data.title,
                description=event_data.description,
                start_time=event_data.start_time,
                end_time=event_data.end_time,
                location=event_data.location,
                tags=tags_json,
                is_all_day=event_data.is_all_day,
                reminder_minutes=event_data.reminder_minutes,
                recurrence_rule=event_data.recurrence_rule,
                color=event_data.color
            )
            
            db.add(new_event)
            db.commit()
            db.refresh(new_event)
            
            # Convert to response format
            event_dict = {
                "id": new_event.id,
                "user_id": new_event.user_id,
                "title": new_event.title,
                "description": new_event.description,
                "start_time": new_event.start_time,
                "end_time": new_event.end_time,
                "location": new_event.location,
                "tags": json.loads(new_event.tags) if new_event.tags else [],
                "is_all_day": new_event.is_all_day,
                "reminder_minutes": new_event.reminder_minutes,
                "recurrence_rule": new_event.recurrence_rule,
                "color": new_event.color,
                "created_at": new_event.created_at,
                "updated_at": new_event.updated_at
            }
            
            return {"data": event_dict}
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create event: {str(e)}"
            )

    @staticmethod
    def get_event_by_id(db: Session, user: User, event_id: UUID) -> dict:
        """Get a specific event by ID"""
        event = db.query(Event).filter(
            and_(Event.id == event_id, Event.user_id == user.id)
        ).first()
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        # Convert to response format
        event_dict = {
            "id": event.id,
            "user_id": event.user_id,
            "title": event.title,
            "description": event.description,
            "start_time": event.start_time,
            "end_time": event.end_time,
            "location": event.location,
            "tags": json.loads(event.tags) if event.tags else [],
            "is_all_day": event.is_all_day,
            "reminder_minutes": event.reminder_minutes,
            "recurrence_rule": event.recurrence_rule,
            "color": event.color,
            "created_at": event.created_at,
            "updated_at": event.updated_at
        }
        
        return {"data": event_dict}

    @staticmethod
    def update_event(db: Session, user: User, event_id: UUID, event_data: EventUpdate) -> dict:
        """Update an existing event"""
        event = db.query(Event).filter(
            and_(Event.id == event_id, Event.user_id == user.id)
        ).first()
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        try:
            # Update only provided fields
            update_data = event_data.dict(exclude_unset=True)
            
            # Handle tags conversion
            if 'tags' in update_data:
                update_data['tags'] = json.dumps(update_data['tags']) if update_data['tags'] else None
            
            for field, value in update_data.items():
                setattr(event, field, value)
            
            db.commit()
            db.refresh(event)
            
            # Convert to response format
            event_dict = {
                "id": event.id,
                "user_id": event.user_id,
                "title": event.title,
                "description": event.description,
                "start_time": event.start_time,
                "end_time": event.end_time,
                "location": event.location,
                "tags": json.loads(event.tags) if event.tags else [],
                "is_all_day": event.is_all_day,
                "reminder_minutes": event.reminder_minutes,
                "recurrence_rule": event.recurrence_rule,
                "color": event.color,
                "created_at": event.created_at,
                "updated_at": event.updated_at
            }
            
            return {"data": event_dict}
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update event: {str(e)}"
            )

    @staticmethod
    def delete_event(db: Session, user: User, event_id: UUID) -> dict:
        """Delete an event"""
        event = db.query(Event).filter(
            and_(Event.id == event_id, Event.user_id == user.id)
        ).first()
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        try:
            db.delete(event)
            db.commit()
            
            return {"message": "Event deleted successfully"}
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to delete event: {str(e)}"
            )

    @staticmethod
    def get_calendar_view(db: Session, user: User, year: int, month: int) -> dict:
        """Get calendar view for a specific month"""
        # Calculate start and end dates for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        # Get events for the month
        events = db.query(Event).filter(
            and_(
                Event.user_id == user.id,
                or_(
                    and_(Event.start_time >= start_date, Event.start_time <= end_date),
                    and_(Event.end_time >= start_date, Event.end_time <= end_date),
                    and_(Event.start_time <= start_date, Event.end_time >= end_date)
                )
            )
        ).order_by(Event.start_time).all()
        
        # Create calendar structure
        cal = calendar.monthcalendar(year, month)
        calendar_data = {
            "year": year,
            "month": month,
            "month_name": calendar.month_name[month],
            "calendar_grid": cal,
            "events": [],
            "events_by_date": {}
        }
        
        # Process events
        for event in events:
            event_dict = {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "start_time": event.start_time,
                "end_time": event.end_time,
                "location": event.location,
                "tags": json.loads(event.tags) if event.tags else [],
                "is_all_day": event.is_all_day,
                "color": event.color
            }
            calendar_data["events"].append(event_dict)
            
            # Group events by date
            event_date = event.start_time.date().isoformat()
            if event_date not in calendar_data["events_by_date"]:
                calendar_data["events_by_date"][event_date] = []
            calendar_data["events_by_date"][event_date].append(event_dict)
        
        return {"data": calendar_data}

    @staticmethod
    def get_upcoming_events(db: Session, user: User, days: int = 7) -> dict:
        """Get upcoming events for the next N days"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        
        events = db.query(Event).filter(
            and_(
                Event.user_id == user.id,
                Event.start_time >= start_date,
                Event.start_time <= end_date
            )
        ).order_by(Event.start_time).all()
        
        # Convert to response format
        event_data = []
        for event in events:
            event_dict = {
                "id": event.id,
                "user_id": event.user_id,
                "title": event.title,
                "description": event.description,
                "start_time": event.start_time,
                "end_time": event.end_time,
                "location": event.location,
                "tags": json.loads(event.tags) if event.tags else [],
                "is_all_day": event.is_all_day,
                "reminder_minutes": event.reminder_minutes,
                "recurrence_rule": event.recurrence_rule,
                "color": event.color,
                "created_at": event.created_at,
                "updated_at": event.updated_at
            }
            event_data.append(event_dict)
        
        return {
            "data": event_data,
            "meta": {
                "total": len(event_data),
                "days": days,
                "start_date": start_date,
                "end_date": end_date,
                "timestamp": datetime.utcnow()
            }
        }

    @staticmethod
    def parse_natural_language(text: str) -> dict:
        """Parse natural language text into event data (placeholder for AI integration)"""
        # This is a placeholder implementation
        # In a real implementation, this would integrate with an AI service like Google Gemini
        
        # Simple parsing logic as a placeholder
        parsed_data = {
            "title": text[:50] + "..." if len(text) > 50 else text,
            "description": text,
            "start_time": None,
            "end_time": None,
            "location": None,
            "tags": [],
            "is_all_day": False,
            "confidence_score": 0.5
        }
        
        # Basic keyword detection
        if "lunch" in text.lower() or "dinner" in text.lower() or "coffee" in text.lower():
            parsed_data["tags"].append("food")
        if "meeting" in text.lower() or "call" in text.lower():
            parsed_data["tags"].append("work")
        if "tomorrow" in text.lower():
            tomorrow = datetime.now() + timedelta(days=1)
            parsed_data["start_time"] = tomorrow.replace(hour=12, minute=0, second=0, microsecond=0)
            parsed_data["end_time"] = tomorrow.replace(hour=13, minute=0, second=0, microsecond=0)
            parsed_data["confidence_score"] = 0.7
        
        return {"data": parsed_data}

    @staticmethod
    async def parse_text_with_ai(db, user, text: str) -> AIEventParseResponse:
        """Parse event from text using Gemini AI and create event if valid"""
        ai_result = await ai_service.parse_text_event(text)
        if not ai_result.get('is_event_related', True):
            return AIEventParseResponse(success=False, parsed_data=ai_result, message=ai_result.get('message', 'Not event related'))
        # Validate required fields
        if not ai_result.get('title') or not ai_result.get('start_time') or not ai_result.get('end_time'):
            return AIEventParseResponse(success=False, parsed_data=ai_result, message='Missing required fields')
        # Build EventCreate
        event_data = EventCreate(
            title=ai_result['title'],
            description=ai_result.get('description'),
            start_time=ai_result['start_time'],
            end_time=ai_result['end_time'],
            location=ai_result.get('location'),
            tags=ai_result.get('tags', []),
            is_all_day=ai_result.get('is_all_day', False),
            reminder_minutes=ai_result.get('reminder_minutes'),
            recurrence_rule=ai_result.get('recurrence_rule'),
            color=ai_result.get('color')
        )
        created = EventService.create_event(db, user, event_data)
        return AIEventParseResponse(success=True, data=EventOut(**created['data']), parsed_data=ai_result, confidence=ai_result.get('confidence'), message='Event created successfully')

    @staticmethod
    async def parse_voice_with_ai(db, user, file) -> AIEventParseResponse:
        """Parse event from voice using Gemini AI and create event if valid"""
        ai_result = await ai_service.parse_voice_event(file)
        if not ai_result.get('is_event_related', True):
            return AIEventParseResponse(success=False, parsed_data=ai_result, transcribed_text=ai_result.get('transcribed_text'), message=ai_result.get('message', 'Not event related'))
        # Validate required fields
        if not ai_result.get('title') or not ai_result.get('start_time') or not ai_result.get('end_time'):
            return AIEventParseResponse(success=False, parsed_data=ai_result, transcribed_text=ai_result.get('transcribed_text'), message='Missing required fields')
        # Build EventCreate
        event_data = EventCreate(
            title=ai_result['title'],
            description=ai_result.get('description'),
            start_time=ai_result['start_time'],
            end_time=ai_result['end_time'],
            location=ai_result.get('location'),
            tags=ai_result.get('tags', []),
            is_all_day=ai_result.get('is_all_day', False),
            reminder_minutes=ai_result.get('reminder_minutes'),
            recurrence_rule=ai_result.get('recurrence_rule'),
            color=ai_result.get('color')
        )
        created = EventService.create_event(db, user, event_data)
        return AIEventParseResponse(success=True, data=EventOut(**created['data']), parsed_data=ai_result, confidence=ai_result.get('confidence'), transcribed_text=ai_result.get('transcribed_text'), message='Event created successfully')
