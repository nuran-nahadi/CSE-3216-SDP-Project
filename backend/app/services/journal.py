from sqlalchemy.orm import Session
from sqlalchemy import and_, extract, func, desc, or_
from fastapi import HTTPException, status
from app.models.models import JournalEntry, User
from app.schemas.journal import JournalEntryCreate, JournalEntryUpdate, JournalEntryOut, JournalParseRequest
from typing import List, Optional
from datetime import datetime, date, timedelta
import json
from uuid import UUID
import calendar


class JournalService:
    
    @staticmethod
    def get_entries(
        db: Session, 
        user: User, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        mood: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> dict:
        """Get journal entries with filters and pagination"""
        query = db.query(JournalEntry).filter(JournalEntry.user_id == user.id)
        
        # Apply filters
        if start_date:
            query = query.filter(JournalEntry.created_at >= start_date)
        if end_date:
            query = query.filter(JournalEntry.created_at <= end_date)
        if mood:
            query = query.filter(JournalEntry.mood == mood)
        if search:
            query = query.filter(
                or_(
                    JournalEntry.title.ilike(f"%{search}%"),
                    JournalEntry.content.ilike(f"%{search}%"),
                    JournalEntry.summary.ilike(f"%{search}%")
                )
            )
        
        # Order by creation date (newest first)
        query = query.order_by(desc(JournalEntry.created_at))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        entries = query.offset(offset).limit(limit).all()
        
        # Calculate pagination info
        total_pages = (total + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            "data": entries,
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            }
        }
    
    @staticmethod
    def create_entry(db: Session, user: User, entry_data: JournalEntryCreate) -> JournalEntry:
        """Create a new journal entry"""
        entry = JournalEntry(
            user_id=user.id,
            title=entry_data.title,
            content=entry_data.content,
            mood=entry_data.mood,
            weather=entry_data.weather,
            location=entry_data.location
        )
        
        # TODO: Add AI analysis here
        # entry.sentiment_score = analyze_sentiment(entry_data.content)
        # entry.keywords = json.dumps(extract_keywords(entry_data.content))
        # entry.summary = generate_summary(entry_data.content)
        
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    
    @staticmethod
    def get_entry_by_id(db: Session, user: User, entry_id: UUID) -> JournalEntry:
        """Get a specific journal entry by ID"""
        entry = db.query(JournalEntry).filter(
            and_(JournalEntry.id == entry_id, JournalEntry.user_id == user.id)
        ).first()
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journal entry not found"
            )
        return entry
    
    @staticmethod
    def update_entry(db: Session, user: User, entry_id: UUID, entry_data: JournalEntryUpdate) -> JournalEntry:
        """Update a journal entry"""
        entry = JournalService.get_entry_by_id(db, user, entry_id)
        
        # Update fields if provided
        if entry_data.title is not None:
            entry.title = entry_data.title
        if entry_data.content is not None:
            entry.content = entry_data.content
            # TODO: Re-analyze content if it changed
            # entry.sentiment_score = analyze_sentiment(entry_data.content)
            # entry.keywords = json.dumps(extract_keywords(entry_data.content))
            # entry.summary = generate_summary(entry_data.content)
        if entry_data.mood is not None:
            entry.mood = entry_data.mood
        if entry_data.weather is not None:
            entry.weather = entry_data.weather
        if entry_data.location is not None:
            entry.location = entry_data.location
        
        db.commit()
        db.refresh(entry)
        return entry
    
    @staticmethod
    def delete_entry(db: Session, user: User, entry_id: UUID) -> bool:
        """Delete a journal entry"""
        entry = JournalService.get_entry_by_id(db, user, entry_id)
        db.delete(entry)
        db.commit()
        return True
    
    @staticmethod
    def parse_natural_language(text: str) -> dict:
        """Parse natural language input into journal entry data"""
        # TODO: Implement AI parsing
        # For now, return basic parsing
        return {
            "title": None,
            "content": text,
            "mood": None,
            "weather": None,
            "location": None
        }
    
    @staticmethod
    def analyze_entries(db: Session, user: User, entry_ids: Optional[List[UUID]] = None) -> dict:
        """Trigger AI analysis for journal entries"""
        query = db.query(JournalEntry).filter(JournalEntry.user_id == user.id)
        
        if entry_ids:
            query = query.filter(JournalEntry.id.in_(entry_ids))
        
        entries = query.all()
        
        # TODO: Implement AI analysis
        analyzed_count = len(entries)
        
        return {
            "analyzed_entries": analyzed_count,
            "message": f"Analysis triggered for {analyzed_count} entries"
        }
    
    @staticmethod
    def get_journal_stats(db: Session, user: User) -> dict:
        """Get journaling statistics"""
        total_entries = db.query(JournalEntry).filter(JournalEntry.user_id == user.id).count()
        
        # Get entries this month
        current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        entries_this_month = db.query(JournalEntry).filter(
            and_(
                JournalEntry.user_id == user.id,
                JournalEntry.created_at >= current_month
            )
        ).count()
        
        # Get mood distribution
        mood_stats = db.query(
            JournalEntry.mood,
            func.count(JournalEntry.mood).label('count')
        ).filter(JournalEntry.user_id == user.id).group_by(JournalEntry.mood).all()
        
        mood_distribution = {mood: count for mood, count in mood_stats if mood}
        
        # Get average sentiment score
        avg_sentiment = db.query(func.avg(JournalEntry.sentiment_score)).filter(
            and_(
                JournalEntry.user_id == user.id,
                JournalEntry.sentiment_score.isnot(None)
            )
        ).scalar()
        
        # Calculate longest streak
        entries_by_date = db.query(
            func.date(JournalEntry.created_at).label('date')
        ).filter(JournalEntry.user_id == user.id).distinct().order_by('date').all()
        
        longest_streak = JournalService._calculate_longest_streak([entry.date for entry in entries_by_date])
        
        return {
            "total_entries": total_entries,
            "entries_this_month": entries_this_month,
            "mood_distribution": mood_distribution,
            "average_sentiment": round(avg_sentiment, 3) if avg_sentiment else None,
            "longest_streak": longest_streak
        }
    
    @staticmethod
    def get_mood_trends(db: Session, user: User, days: int = 30) -> dict:
        """Get mood trends over time"""
        start_date = datetime.now() - timedelta(days=days)
        
        mood_trends = db.query(
            func.date(JournalEntry.created_at).label('date'),
            JournalEntry.mood,
            func.avg(JournalEntry.sentiment_score).label('avg_sentiment')
        ).filter(
            and_(
                JournalEntry.user_id == user.id,
                JournalEntry.created_at >= start_date
            )
        ).group_by(
            func.date(JournalEntry.created_at),
            JournalEntry.mood
        ).order_by('date').all()
        
        # Group by date
        trends_by_date = {}
        for trend in mood_trends:
            date_str = trend.date.isoformat()
            if date_str not in trends_by_date:
                trends_by_date[date_str] = []
            trends_by_date[date_str].append({
                "mood": trend.mood,
                "avg_sentiment": round(trend.avg_sentiment, 3) if trend.avg_sentiment else None
            })
        
        return {
            "trends": trends_by_date,
            "period_days": days,
            "start_date": start_date.date().isoformat(),
            "end_date": datetime.now().date().isoformat()
        }
    
    @staticmethod
    def _calculate_longest_streak(dates: List[date]) -> int:
        """Calculate the longest consecutive streak of journal entries"""
        if not dates:
            return 0
        
        dates = sorted(set(dates))  # Remove duplicates and sort
        longest = 1
        current = 1
        
        for i in range(1, len(dates)):
            if (dates[i] - dates[i-1]).days == 1:
                current += 1
                longest = max(longest, current)
            else:
                current = 1
        
        return longest
