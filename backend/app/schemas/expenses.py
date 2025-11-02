from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID
from enum import Enum
import json


class BaseConfig:
    from_attributes = True


# Enums for expenses
class ExpenseCategory(str, Enum):
    food = "food"
    transport = "transport"
    entertainment = "entertainment"
    bills = "bills"
    shopping = "shopping"
    health = "health"
    education = "education"
    travel = "travel"
    other = "other"


class PaymentMethod(str, Enum):
    cash = "cash"
    credit_card = "credit_card"
    debit_card = "debit_card"
    bank_transfer = "bank_transfer"
    digital_wallet = "digital_wallet"
    other = "other"


# Base expense schema
class ExpenseBase(BaseModel):
    amount: float
    currency: str = "Taka"
    category: ExpenseCategory
    subcategory: Optional[str] = None
    merchant: Optional[str] = None
    description: Optional[str] = None
    date: datetime
    payment_method: Optional[PaymentMethod] = None
    receipt_url: Optional[str] = None
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None
    tags: Optional[List[str]] = None

    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v or []

    class Config(BaseConfig):
        pass


# Create expense schema
class ExpenseCreate(BaseModel):
    amount: float
    currency: str = "Taka"
    category: ExpenseCategory
    subcategory: Optional[str] = None
    merchant: Optional[str] = None
    description: Optional[str] = None
    date: datetime
    payment_method: Optional[PaymentMethod] = None
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None
    tags: Optional[List[str]] = None

    class Config(BaseConfig):
        pass


# Update expense schema
class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    currency: Optional[str] = None
    category: Optional[ExpenseCategory] = None
    subcategory: Optional[str] = None
    merchant: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    payment_method: Optional[PaymentMethod] = None
    is_recurring: Optional[bool] = None
    recurrence_rule: Optional[str] = None
    tags: Optional[List[str]] = None

    class Config(BaseConfig):
        pass


# Expense output schema
class ExpenseOut(ExpenseBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        elif isinstance(v, dict):
            # Handle case where tags is stored as a dict like {'tags': ['value1', 'value2']}
            if 'tags' in v:
                return v['tags'] if isinstance(v['tags'], list) else []
            return []
        elif isinstance(v, list):
            return v
        return v or []

    class Config(BaseConfig):
        pass


# Parse natural language expense
class ExpenseParseRequest(BaseModel):
    text: str

    class Config(BaseConfig):
        pass


# Expense summary schemas
class CategorySummary(BaseModel):
    category: str
    total_amount: float
    count: int
    percentage: float

    class Config(BaseConfig):
        pass


class ExpenseSummary(BaseModel):
    total_amount: float
    total_count: int
    average_amount: float
    categories: List[CategorySummary]
    period_start: datetime
    period_end: datetime

    class Config(BaseConfig):
        pass


# Monthly expense schema
class MonthlyExpense(BaseModel):
    year: int
    month: int
    total_amount: float
    count: int
    categories: List[CategorySummary]

    class Config(BaseConfig):
        pass


# Bulk import schema
class ExpenseBulkImport(BaseModel):
    expenses: List[ExpenseCreate]

    class Config(BaseConfig):
        pass


# Response schemas
class ExpenseResponse(BaseModel):
    success: bool
    data: ExpenseOut
    message: str

    class Config(BaseConfig):
        pass


class ExpensesResponse(BaseModel):
    success: bool
    data: List[ExpenseOut]
    message: str
    meta: Optional[dict] = None

    class Config(BaseConfig):
        pass


class ExpenseSummaryResponse(BaseModel):
    success: bool
    data: ExpenseSummary
    message: str

    class Config(BaseConfig):
        pass


class MonthlyExpenseResponse(BaseModel):
    success: bool
    data: MonthlyExpense
    message: str

    class Config(BaseConfig):
        pass


class CategoriesResponse(BaseModel):
    success: bool
    data: List[CategorySummary]
    message: str

    class Config(BaseConfig):
        pass


class MessageResponse(BaseModel):
    success: bool
    message: str

    class Config(BaseConfig):
        pass


# AI parsing schemas
class AIExpenseParseRequest(BaseModel):
    """Schema for AI expense parsing from text"""
    text: str
    
    class Config(BaseConfig):
        pass


class AIExpenseParseResponse(BaseModel):
    """Response schema for AI-parsed expense"""
    success: bool
    data: Optional[ExpenseOut] = None
    parsed_data: Optional[dict] = None
    confidence: Optional[float] = None
    transcribed_text: Optional[str] = None  # For voice inputs
    message: str
    
    class Config(BaseConfig):
        pass


class AIInsightsResponse(BaseModel):
    """Response schema for AI-generated spending insights"""
    success: bool
    data: dict
    message: str
    
    class Config(BaseConfig):
        pass


# Dashboard Analytics Schemas
class TotalSpendData(BaseModel):
    """Schema for total spend data"""
    current_month: float
    previous_month: float
    percentage_change: float
    change_direction: str  # "increase", "decrease", "same"
    
    class Config(BaseConfig):
        pass


class CategoryBreakdownItem(BaseModel):
    """Schema for category breakdown item"""
    category: str
    amount: float
    percentage: float
    transaction_count: int
    
    class Config(BaseConfig):
        pass


class CategoryTrendMonth(BaseModel):
    """Schema for category trend in a specific month"""
    month: str  # Format: "2025-01"
    category: str
    amount: float
    percentage: float
    
    class Config(BaseConfig):
        pass


class SpendTrendData(BaseModel):
    """Schema for spend trend data point"""
    date: str  # Format depends on period: "2025-01-15" for daily, "2025-W03" for weekly, "2025-01" for monthly
    amount: float
    transaction_count: int
    
    class Config(BaseConfig):
        pass


class TopTransactionData(BaseModel):
    """Schema for top transaction data"""
    id: UUID
    amount: float
    category: str
    merchant: Optional[str]
    description: Optional[str]
    date: datetime
    
    class Config(BaseConfig):
        pass


# Dashboard Response Schemas
class TotalSpendResponse(BaseModel):
    """Response schema for total spend dashboard data"""
    success: bool
    data: TotalSpendData
    message: str
    
    class Config(BaseConfig):
        pass


class CategoryBreakdownResponse(BaseModel):
    """Response schema for category breakdown dashboard data"""
    success: bool
    data: List[CategoryBreakdownItem]
    message: str
    
    class Config(BaseConfig):
        pass


class CategoryTrendResponse(BaseModel):
    """Response schema for category trend dashboard data"""
    success: bool
    data: List[CategoryTrendMonth]
    message: str
    
    class Config(BaseConfig):
        pass


class SpendTrendResponse(BaseModel):
    """Response schema for spend trend dashboard data"""
    success: bool
    data: List[SpendTrendData]
    message: str
    
    class Config(BaseConfig):
        pass


class TopTransactionsResponse(BaseModel):
    """Response schema for top transactions dashboard data"""
    success: bool
    data: List[TopTransactionData]
    message: str
    
    class Config(BaseConfig):
        pass
