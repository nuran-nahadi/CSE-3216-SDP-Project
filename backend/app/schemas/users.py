from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from enum import Enum
from pydantic import field_validator
import json


class BaseConfig:
    from_attributes = True


# Enums for preferences
class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Theme(str, Enum):
    light = "light"
    dark = "dark"
    auto = "auto"


class TimeFormat(str, Enum):
    twelve_hour = "12h"
    twenty_four_hour = "24h"


class WeekStartDay(str, Enum):
    monday = "monday"
    sunday = "sunday"


# User Models
class UserBase(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    is_verified: bool
    profile_picture_url: Optional[str] = None
    timezone: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config(BaseConfig):
        pass


class UserProfileOut(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    is_verified: bool
    profile_picture_url: Optional[str] = None
    timezone: str
    created_at: datetime
    updated_at: datetime

    class Config(BaseConfig):
        pass


class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    timezone: Optional[str] = None

    class Config(BaseConfig):
        pass


# User Preferences Models
class UserPreferencesBase(BaseModel):
    default_task_priority: TaskPriority = TaskPriority.medium
    default_expense_currency: str = "USD"
    notification_settings: Optional[dict] = None
    theme: Theme = Theme.auto
    language: str = "en"
    date_format: str = "YYYY-MM-DD"
    time_format: TimeFormat = TimeFormat.twelve_hour
    week_start_day: WeekStartDay = WeekStartDay.monday
    ai_insights_enabled: bool = True

    class Config(BaseConfig):
        pass


class UserPreferencesOut(UserPreferencesBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    @field_validator('notification_settings', mode='before')
    @classmethod
    def parse_notification_settings(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v

    class Config(BaseConfig):
        pass


class UserPreferencesUpdate(BaseModel):
    default_task_priority: Optional[TaskPriority] = None
    default_expense_currency: Optional[str] = None
    notification_settings: Optional[dict] = None
    theme: Optional[Theme] = None
    language: Optional[str] = None
    date_format: Optional[str] = None
    time_format: Optional[TimeFormat] = None
    week_start_day: Optional[WeekStartDay] = None
    ai_insights_enabled: Optional[bool] = None

    class Config(BaseConfig):
        pass


# Legacy schemas for backward compatibility
class UserCreate(BaseModel):
    full_name: str
    username: str
    email: str
    password: str

    class Config(BaseConfig):
        pass


class UserUpdate(UserCreate):
    pass


class UserOut(BaseModel):
    message: str
    data: UserBase

    class Config(BaseConfig):
        pass


class UsersOut(BaseModel):
    message: str
    data: List[UserBase]

    class Config(BaseConfig):
        pass


class UserOutDelete(BaseModel):
    message: str
    data: UserBase

    class Config(BaseConfig):
        pass


# Response schemas for user profile endpoints
class UserProfileResponse(BaseModel):
    success: bool
    data: UserProfileOut
    message: str

    class Config(BaseConfig):
        pass


class UserPreferencesResponse(BaseModel):
    success: bool
    data: UserPreferencesOut
    message: str

    class Config(BaseConfig):
        pass


class MessageResponse(BaseModel):
    success: bool
    message: str

    class Config(BaseConfig):
        pass
