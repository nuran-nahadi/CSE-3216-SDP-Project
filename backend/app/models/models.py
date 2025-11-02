from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Float, ARRAY, Enum, Text
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, server_default="False", nullable=False)
    profile_picture_url = Column(String, nullable=True)
    timezone = Column(String, server_default="UTC", nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=False)
    
    # Keep role for backward compatibility
    role = Column(Enum("admin", "user", name="user_roles"), nullable=False, server_default="user")
    # Keep is_active for backward compatibility  
    is_active = Column(Boolean, server_default="True", nullable=False)


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    default_task_priority = Column(Enum("low", "medium", "high", name="task_priorities"), server_default="medium", nullable=False)
    default_expense_currency = Column(String, server_default="USD", nullable=False)
    notification_settings = Column(String, nullable=True)  # JSON stored as string
    theme = Column(Enum("light", "dark", "auto", name="themes"), server_default="auto", nullable=False)
    language = Column(String, server_default="en", nullable=False)
    date_format = Column(String, server_default="YYYY-MM-DD", nullable=False)
    time_format = Column(Enum("12h", "24h", name="time_formats"), server_default="12h", nullable=False)
    week_start_day = Column(Enum("monday", "sunday", name="week_start_days"), server_default="monday", nullable=False)
    ai_insights_enabled = Column(Boolean, server_default="True", nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=False)
    
    # Relationship
    user = relationship("User", backref="preferences")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)  # Using Float instead of Decimal for simplicity
    currency = Column(String, server_default="Taka", nullable=False)
    category = Column(Enum(
        "food", "transport", "entertainment", "bills", "shopping", 
        "health", "education", "travel", "other", 
        name="expense_categories"
    ), nullable=False)
    subcategory = Column(String, nullable=True)
    merchant = Column(String, nullable=True)
    description = Column(String, nullable=True)  # Text equivalent
    date = Column(TIMESTAMP(timezone=True), nullable=False)
    payment_method = Column(Enum(
        "cash", "credit_card", "debit_card", "bank_transfer", 
        "digital_wallet", "other", 
        name="payment_methods"
    ), nullable=True)
    receipt_url = Column(String, nullable=True)
    is_recurring = Column(Boolean, server_default="False", nullable=False)
    recurrence_rule = Column(String, nullable=True)
    tags = Column(String, nullable=True)  # JSON stored as string
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=False)
    
    # Relationship
    user = relationship("User", backref="expenses")


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(TIMESTAMP(timezone=True), nullable=False)
    end_time = Column(TIMESTAMP(timezone=True), nullable=False)
    location = Column(String, nullable=True)
    tags = Column(String, nullable=True)  # JSON stored as string
    is_all_day = Column(Boolean, server_default="False", nullable=False)
    reminder_minutes = Column(Integer, nullable=True)
    recurrence_rule = Column(String, nullable=True)
    color = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=False)
    
    # Relationship
    user = relationship("User", backref="events")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(TIMESTAMP(timezone=True), nullable=True)
    priority = Column(Enum("low", "medium", "high", name="task_priorities"), server_default="medium", nullable=False)
    status = Column(Enum("pending", "in_progress", "completed", "cancelled", name="task_statuses"), server_default="pending", nullable=False)
    is_completed = Column(Boolean, server_default="False", nullable=False)
    completion_date = Column(TIMESTAMP(timezone=True), nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # in minutes
    actual_duration = Column(Integer, nullable=True)  # in minutes
    tags = Column(String, nullable=True)  # JSON stored as string
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=False)
    
    # Relationships
    user = relationship("User", backref="tasks")
    subtasks = relationship("Task", backref="parent_task", remote_side=[id])


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    mood = Column(Enum(
        "very_happy", "happy", "neutral", "sad", "very_sad", 
        "angry", "excited", "anxious", "grateful", 
        name="journal_moods"
    ), nullable=True)
    sentiment_score = Column(Float, nullable=True)  # Range: -1.0 to 1.0
    keywords = Column(String, nullable=True)  # JSON stored as string
    summary = Column(Text, nullable=True)
    weather = Column(String, nullable=True)
    location = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=False)
    
    # Relationship
    user = relationship("User", backref="journal_entries")
