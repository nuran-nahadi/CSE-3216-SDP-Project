# FastAPI Design Patterns Refactoring Guide

## Table of Contents
1. [Current Architecture Analysis](#current-architecture-analysis)
2. [Design Patterns to Implement](#design-patterns-to-implement)
3. [Refactoring Strategy](#refactoring-strategy)
4. [Implementation Plan](#implementation-plan)
5. [Code Examples](#code-examples)
6. [Benefits and Trade-offs](#benefits-and-trade-offs)
7. [Testing Strategy](#testing-strategy)

## Current Architecture Analysis

### Current Structure
Your FastAPI application follows a layered architecture with:
- **Routers**: Handle HTTP requests and responses
- **Services**: Business logic implementation
- **Models**: SQLAlchemy ORM models
- **Schemas**: Pydantic models for validation
- **Core**: Configuration and security utilities
- **Database**: Connection and session management

### Current Patterns (Already Implemented)
1. **Layered Architecture**: Separation of concerns between routers, services, and data layers
2. **Dependency Injection**: FastAPI's dependency system for database sessions and authentication
3. **Repository Pattern** (Partial): Service classes act as repositories for database operations
4. **MVC Pattern** (Modified): Controllers (routers), Models (SQLAlchemy), Views (JSON responses)

### Areas for Improvement
- **Code Duplication**: Similar CRUD operations across services
- **Configuration Management**: Settings scattered across modules
- **Error Handling**: Inconsistent error responses
- **Service Dependencies**: Tight coupling between services
- **Resource Management**: No proper connection pooling or caching

---

## Design Patterns to Implement

### 1. Repository Pattern (Enhanced)
**Purpose**: Abstract data access layer and provide a more object-oriented view of the persistence layer.

**Current Issue**: Service classes mix business logic with data access logic.

**Benefits**:
- Better testability with mock repositories
- Cleaner separation of concerns
- Easier to switch between different data sources
- Standardized CRUD operations

### 2. Unit of Work Pattern
**Purpose**: Maintain a list of objects affected by a business transaction and coordinates writing out changes.

**Current Issue**: Manual transaction management in services.

**Benefits**:
- Atomic operations across multiple repositories
- Better transaction management
- Improved data consistency

### 3. Factory Pattern
**Purpose**: Create objects without specifying their exact classes.

**Applications**:
- Service factory for different AI providers
- Repository factory for different data sources
- Response factory for different response types

### 4. Strategy Pattern
**Purpose**: Define algorithms and make them interchangeable.

**Applications**:
- Different authentication strategies (JWT, OAuth, API Key)
- Multiple AI service providers (OpenAI, Google Gemini)
- Various file upload strategies (local, cloud storage)
- Different notification methods (email, SMS, push)

### 5. Observer Pattern
**Purpose**: Define a one-to-many dependency between objects.

**Applications**:
- Event-driven architecture for expense tracking
- Notification system for task reminders
- Audit logging for user actions
- Real-time updates for dashboard metrics

### 6. Decorator Pattern
**Purpose**: Add behavior to objects dynamically without altering their structure.

**Applications**:
- Caching decorators for expensive operations
- Logging decorators for service methods
- Rate limiting decorators for API endpoints
- Validation decorators for business rules

### 7. Command Pattern
**Purpose**: Encapsulate requests as objects.

**Applications**:
- API operation commands for undo/redo functionality
- Batch processing of expenses/tasks
- Queue-based task processing
- Database migration commands

### 8. Adapter Pattern
**Purpose**: Allow incompatible interfaces to work together.

**Applications**:
- Third-party API integrations (payment gateways, cloud services)
- Legacy system integration
- Multiple database adapters

### 9. Singleton Pattern
**Purpose**: Ensure a class has only one instance.

**Applications**:
- Database connection manager
- Configuration manager
- Logger instance
- Cache manager

### 10. Template Method Pattern
**Purpose**: Define the skeleton of an algorithm in a base class.

**Applications**:
- CRUD operation templates
- API response formatting
- Data validation workflows
- Report generation templates

---

## Refactoring Strategy

### Phase 1: Infrastructure Patterns (Weeks 1-2)
1. **Singleton Pattern**: Configuration and connection management
2. **Factory Pattern**: Service and repository creation
3. **Adapter Pattern**: External service integrations

### Phase 2: Data Access Patterns (Weeks 3-4)
1. **Repository Pattern**: Enhanced data access layer
2. **Unit of Work Pattern**: Transaction management
3. **Template Method Pattern**: CRUD operations

### Phase 3: Behavioral Patterns (Weeks 5-6)
1. **Strategy Pattern**: Authentication and AI services
2. **Observer Pattern**: Event-driven features
3. **Command Pattern**: Operation encapsulation

### Phase 4: Structural Patterns (Weeks 7-8)
1. **Decorator Pattern**: Cross-cutting concerns
2. **Facade Pattern**: Simplified interfaces
3. **Bridge Pattern**: Abstraction implementation separation

---

## Implementation Plan

### 1. Repository Pattern Implementation

#### Step 1: Create Base Repository Interface
```python
# app/repositories/base.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from uuid import UUID

T = TypeVar('T')

class BaseRepository(Generic[T], ABC):
    def __init__(self, db: Session, model_class: type):
        self.db = db
        self.model_class = model_class
    
    @abstractmethod
    def create(self, obj_data: Dict[str, Any]) -> T:
        pass
    
    @abstractmethod
    def get_by_id(self, obj_id: UUID) -> Optional[T]:
        pass
    
    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100, **filters) -> List[T]:
        pass
    
    @abstractmethod
    def update(self, obj_id: UUID, obj_data: Dict[str, Any]) -> Optional[T]:
        pass
    
    @abstractmethod
    def delete(self, obj_id: UUID) -> bool:
        pass
    
    @abstractmethod
    def count(self, **filters) -> int:
        pass
```

#### Step 2: Implement Concrete Repositories
```python
# app/repositories/expense_repository.py
from app.repositories.base import BaseRepository
from app.models.models import Expense
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class ExpenseRepository(BaseRepository[Expense]):
    
    def create(self, obj_data: Dict[str, Any]) -> Expense:
        expense = self.model_class(**obj_data)
        self.db.add(expense)
        self.db.commit()
        self.db.refresh(expense)
        return expense
    
    def get_by_id(self, obj_id: UUID) -> Optional[Expense]:
        return self.db.query(self.model_class).filter(
            self.model_class.id == obj_id
        ).first()
    
    def get_all(self, skip: int = 0, limit: int = 100, **filters) -> List[Expense]:
        query = self.db.query(self.model_class)
        
        # Apply filters
        if 'user_id' in filters:
            query = query.filter(self.model_class.user_id == filters['user_id'])
        if 'start_date' in filters:
            query = query.filter(self.model_class.date >= filters['start_date'])
        if 'end_date' in filters:
            query = query.filter(self.model_class.date <= filters['end_date'])
        if 'category' in filters:
            query = query.filter(self.model_class.category == filters['category'])
        
        return query.offset(skip).limit(limit).all()
    
    def update(self, obj_id: UUID, obj_data: Dict[str, Any]) -> Optional[Expense]:
        expense = self.get_by_id(obj_id)
        if expense:
            for key, value in obj_data.items():
                setattr(expense, key, value)
            self.db.commit()
            self.db.refresh(expense)
        return expense
    
    def delete(self, obj_id: UUID) -> bool:
        expense = self.get_by_id(obj_id)
        if expense:
            self.db.delete(expense)
            self.db.commit()
            return True
        return False
    
    def count(self, **filters) -> int:
        query = self.db.query(self.model_class)
        # Apply same filters as get_all
        return query.count()
    
    def get_by_user_and_date_range(
        self, 
        user_id: UUID, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Expense]:
        return self.db.query(self.model_class).filter(
            self.model_class.user_id == user_id,
            self.model_class.date >= start_date,
            self.model_class.date <= end_date
        ).all()
```

### 2. Unit of Work Pattern Implementation

```python
# app/core/unit_of_work.py
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.models.models import Expense, Task, User

class AbstractUnitOfWork(ABC):
    expenses: ExpenseRepository
    tasks: TaskRepository
    users: UserRepository
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.rollback()
    
    @abstractmethod
    def commit(self):
        raise NotImplementedError
    
    @abstractmethod
    def rollback(self):
        raise NotImplementedError

class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, db: Session):
        self.db = db
        self.expenses = ExpenseRepository(db, Expense)
        self.tasks = TaskRepository(db, Task)
        self.users = UserRepository(db, User)
    
    def commit(self):
        self.db.commit()
    
    def rollback(self):
        self.db.rollback()
```

### 3. Factory Pattern Implementation

```python
# app/factories/service_factory.py
from abc import ABC, abstractmethod
from app.services.ai_service import GeminiAIService, OpenAIService
from app.core.config import settings

class AIServiceFactory(ABC):
    @abstractmethod
    def create_ai_service(self) -> Any:
        pass

class GeminiAIServiceFactory(AIServiceFactory):
    def create_ai_service(self) -> GeminiAIService:
        return GeminiAIService()

class OpenAIServiceFactory(AIServiceFactory):
    def create_ai_service(self) -> OpenAIService:
        return OpenAIService()

class AIServiceFactoryProvider:
    @staticmethod
    def get_factory(provider: str) -> AIServiceFactory:
        if provider == "gemini":
            return GeminiAIServiceFactory()
        elif provider == "openai":
            return OpenAIServiceFactory()
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")

# app/factories/repository_factory.py
from sqlalchemy.orm import Session
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.task_repository import TaskRepository
from app.models.models import Expense, Task

class RepositoryFactory:
    def __init__(self, db: Session):
        self.db = db
    
    def create_expense_repository(self) -> ExpenseRepository:
        return ExpenseRepository(self.db, Expense)
    
    def create_task_repository(self) -> TaskRepository:
        return TaskRepository(self.db, Task)
```

### 4. Strategy Pattern Implementation

```python
# app/strategies/auth_strategy.py
from abc import ABC, abstractmethod
from typing import Optional
from app.models.models import User

class AuthenticationStrategy(ABC):
    @abstractmethod
    def authenticate(self, credentials: dict) -> Optional[User]:
        pass

class JWTAuthStrategy(AuthenticationStrategy):
    def authenticate(self, credentials: dict) -> Optional[User]:
        # JWT authentication logic
        pass

class APIKeyAuthStrategy(AuthenticationStrategy):
    def authenticate(self, credentials: dict) -> Optional[User]:
        # API key authentication logic
        pass

class OAuthStrategy(AuthenticationStrategy):
    def authenticate(self, credentials: dict) -> Optional[User]:
        # OAuth authentication logic
        pass

# app/strategies/notification_strategy.py
class NotificationStrategy(ABC):
    @abstractmethod
    def send_notification(self, recipient: str, message: str) -> bool:
        pass

class EmailNotificationStrategy(NotificationStrategy):
    def send_notification(self, recipient: str, message: str) -> bool:
        # Email sending logic
        pass

class SMSNotificationStrategy(NotificationStrategy):
    def send_notification(self, recipient: str, message: str) -> bool:
        # SMS sending logic
        pass
```

### 5. Observer Pattern Implementation

```python
# app/observers/base_observer.py
from abc import ABC, abstractmethod
from typing import Any, List

class Observer(ABC):
    @abstractmethod
    def update(self, event_type: str, data: Any) -> None:
        pass

class Subject:
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)
    
    def notify(self, event_type: str, data: Any) -> None:
        for observer in self._observers:
            observer.update(event_type, data)

# app/observers/expense_observer.py
class ExpenseCreatedObserver(Observer):
    def update(self, event_type: str, data: Any) -> None:
        if event_type == "expense_created":
            # Update budget tracking
            # Send notifications if over budget
            # Update analytics
            pass

class TaskCompletedObserver(Observer):
    def update(self, event_type: str, data: Any) -> None:
        if event_type == "task_completed":
            # Update productivity metrics
            # Send achievement notifications
            pass
```

### 6. Decorator Pattern Implementation

```python
# app/decorators/caching.py
import functools
import json
from typing import Any, Callable
from app.core.cache import CacheManager

def cache_result(expiration: int = 300):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Create cache key
            cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = CacheManager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            CacheManager.set(cache_key, result, expiration)
            return result
        return wrapper
    return decorator

# app/decorators/logging.py
import functools
import logging
from typing import Any, Callable

def log_execution(logger_name: str = __name__):
    def decorator(func: Callable) -> Callable:
        logger = logging.getLogger(logger_name)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger.info(f"Executing {func.__name__} with args: {args}, kwargs: {kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Successfully executed {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"Error executing {func.__name__}: {str(e)}")
                raise
        return wrapper
    return decorator

# app/decorators/rate_limiting.py
import functools
import time
from typing import Any, Callable, Dict
from fastapi import HTTPException, status

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, key: str, max_requests: int, time_window: int) -> bool:
        current_time = time.time()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests outside time window
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if current_time - req_time < time_window
        ]
        
        # Check if under limit
        if len(self.requests[key]) < max_requests:
            self.requests[key].append(current_time)
            return True
        
        return False

rate_limiter = RateLimiter()

def rate_limit(max_requests: int = 100, time_window: int = 3600):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Extract user identifier (simplified)
            user_id = kwargs.get('current_user', {}).get('id', 'anonymous')
            
            if not rate_limiter.is_allowed(f"{func.__name__}_{user_id}", max_requests, time_window):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### 7. Command Pattern Implementation

```python
# app/commands/base_command.py
from abc import ABC, abstractmethod
from typing import Any

class Command(ABC):
    @abstractmethod
    def execute(self) -> Any:
        pass
    
    @abstractmethod
    def undo(self) -> Any:
        pass

# app/commands/expense_commands.py
from app.commands.base_command import Command
from app.core.unit_of_work import AbstractUnitOfWork
from app.schemas.expenses import ExpenseCreate
from uuid import UUID

class CreateExpenseCommand(Command):
    def __init__(self, uow: AbstractUnitOfWork, expense_data: ExpenseCreate, user_id: UUID):
        self.uow = uow
        self.expense_data = expense_data
        self.user_id = user_id
        self.created_expense = None
    
    def execute(self):
        with self.uow:
            expense_dict = self.expense_data.dict()
            expense_dict['user_id'] = self.user_id
            self.created_expense = self.uow.expenses.create(expense_dict)
            self.uow.commit()
            return self.created_expense
    
    def undo(self):
        if self.created_expense:
            with self.uow:
                self.uow.expenses.delete(self.created_expense.id)
                self.uow.commit()

class UpdateExpenseCommand(Command):
    def __init__(self, uow: AbstractUnitOfWork, expense_id: UUID, expense_data: dict):
        self.uow = uow
        self.expense_id = expense_id
        self.expense_data = expense_data
        self.old_data = None
    
    def execute(self):
        with self.uow:
            # Store old data for undo
            expense = self.uow.expenses.get_by_id(self.expense_id)
            if expense:
                self.old_data = {
                    'amount': expense.amount,
                    'category': expense.category,
                    'description': expense.description,
                    # ... other fields
                }
            
            updated_expense = self.uow.expenses.update(self.expense_id, self.expense_data)
            self.uow.commit()
            return updated_expense
    
    def undo(self):
        if self.old_data:
            with self.uow:
                self.uow.expenses.update(self.expense_id, self.old_data)
                self.uow.commit()

# app/commands/command_invoker.py
from typing import List
from app.commands.base_command import Command

class CommandInvoker:
    def __init__(self):
        self.history: List[Command] = []
    
    def execute_command(self, command: Command):
        result = command.execute()
        self.history.append(command)
        return result
    
    def undo_last(self):
        if self.history:
            command = self.history.pop()
            command.undo()
    
    def undo_all(self):
        while self.history:
            self.undo_last()
```

### 8. Singleton Pattern Implementation

```python
# app/core/singleton.py
class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

# app/core/config_manager.py
from app.core.singleton import SingletonMeta
from app.core.config import settings

class ConfigManager(metaclass=SingletonMeta):
    def __init__(self):
        self._settings = settings
        self._cache = {}
    
    def get(self, key: str, default=None):
        if key in self._cache:
            return self._cache[key]
        
        value = getattr(self._settings, key, default)
        self._cache[key] = value
        return value
    
    def set(self, key: str, value):
        self._cache[key] = value

# app/core/cache.py
import redis
from app.core.singleton import SingletonMeta
from app.core.config_manager import ConfigManager

class CacheManager(metaclass=SingletonMeta):
    def __init__(self):
        config = ConfigManager()
        self.redis_client = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379),
            db=config.get('redis_db', 0)
        )
    
    def get(self, key: str):
        value = self.redis_client.get(key)
        return value.decode() if value else None
    
    def set(self, key: str, value: str, expiration: int = 300):
        self.redis_client.setex(key, expiration, value)
    
    def delete(self, key: str):
        self.redis_client.delete(key)
```

### 9. Refactored Service Layer

```python
# app/services/enhanced_expense_service.py
from app.core.unit_of_work import AbstractUnitOfWork
from app.commands.expense_commands import CreateExpenseCommand, UpdateExpenseCommand
from app.commands.command_invoker import CommandInvoker
from app.decorators.caching import cache_result
from app.decorators.logging import log_execution
from app.decorators.rate_limiting import rate_limit
from app.observers.base_observer import Subject
from app.schemas.expenses import ExpenseCreate, ExpenseUpdate
from uuid import UUID
from typing import List, Dict, Any

class EnhancedExpenseService(Subject):
    def __init__(self, uow: AbstractUnitOfWork):
        super().__init__()
        self.uow = uow
        self.command_invoker = CommandInvoker()
    
    @log_execution()
    @rate_limit(max_requests=50, time_window=3600)
    def create_expense(self, expense_data: ExpenseCreate, user_id: UUID) -> Dict[str, Any]:
        command = CreateExpenseCommand(self.uow, expense_data, user_id)
        expense = self.command_invoker.execute_command(command)
        
        # Notify observers
        self.notify("expense_created", {
            "expense": expense,
            "user_id": user_id
        })
        
        return {
            "success": True,
            "data": expense,
            "message": "Expense created successfully"
        }
    
    @cache_result(expiration=300)
    @log_execution()
    def get_expenses(self, user_id: UUID, **filters) -> Dict[str, Any]:
        with self.uow:
            expenses = self.uow.expenses.get_all(user_id=user_id, **filters)
            total_count = self.uow.expenses.count(user_id=user_id, **filters)
        
        return {
            "success": True,
            "data": expenses,
            "meta": {
                "total": total_count,
                "count": len(expenses)
            }
        }
    
    def update_expense(self, expense_id: UUID, expense_data: ExpenseUpdate) -> Dict[str, Any]:
        command = UpdateExpenseCommand(self.uow, expense_id, expense_data.dict())
        expense = self.command_invoker.execute_command(command)
        
        if expense:
            self.notify("expense_updated", {
                "expense": expense,
                "expense_id": expense_id
            })
        
        return {
            "success": bool(expense),
            "data": expense,
            "message": "Expense updated successfully" if expense else "Expense not found"
        }
    
    def undo_last_operation(self):
        self.command_invoker.undo_last()
```

### 10. Updated Router Implementation

```python
# app/routers/enhanced_expenses.py
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.core.unit_of_work import SqlAlchemyUnitOfWork
from app.services.enhanced_expense_service import EnhancedExpenseService
from app.observers.expense_observer import ExpenseCreatedObserver
from app.schemas.expenses import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.models.models import User
from typing import Optional
from datetime import datetime
from uuid import UUID

router = APIRouter(tags=["Enhanced Expenses"], prefix="/v2/expenses")

def get_expense_service(db: Session = Depends(get_db)) -> EnhancedExpenseService:
    uow = SqlAlchemyUnitOfWork(db)
    service = EnhancedExpenseService(uow)
    
    # Attach observers
    expense_observer = ExpenseCreatedObserver()
    service.attach(expense_observer)
    
    return service

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ExpenseResponse,
    summary="Create new expense (Enhanced)",
    description="Create a new expense entry using enhanced service with design patterns"
)
def create_expense(
    expense_data: ExpenseCreate,
    current_user: User = Depends(get_current_user()),
    expense_service: EnhancedExpenseService = Depends(get_expense_service)
):
    """Create new expense with enhanced patterns"""
    return expense_service.create_expense(expense_data, current_user.id)

@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="List expenses (Enhanced)",
    description="Retrieve expenses with caching and enhanced filtering"
)
def get_expenses(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user()),
    expense_service: EnhancedExpenseService = Depends(get_expense_service)
):
    """List expenses with enhanced service"""
    filters = {
        "start_date": start_date,
        "end_date": end_date,
        "category": category,
        "skip": (page - 1) * limit,
        "limit": limit
    }
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    return expense_service.get_expenses(current_user.id, **filters)

@router.post(
    "/undo",
    status_code=status.HTTP_200_OK,
    summary="Undo last operation",
    description="Undo the last expense operation using command pattern"
)
def undo_last_operation(
    expense_service: EnhancedExpenseService = Depends(get_expense_service)
):
    """Undo last expense operation"""
    expense_service.undo_last_operation()
    return {"success": True, "message": "Last operation undone successfully"}
```

---

## Benefits and Trade-offs

### Benefits

#### 1. **Improved Maintainability**
- **Clear Separation of Concerns**: Each pattern addresses specific responsibilities
- **Consistent Code Structure**: Standardized approaches across the application
- **Easier Debugging**: Well-defined interfaces and clear data flow

#### 2. **Enhanced Testability**
- **Mock-friendly Architecture**: Repository and strategy patterns enable easy mocking
- **Isolated Business Logic**: Services focus on business rules, not infrastructure
- **Command Pattern**: Easy to test individual operations and undo functionality

#### 3. **Better Scalability**
- **Horizontal Scaling**: Observer pattern supports distributed event handling
- **Performance Optimization**: Decorator pattern for caching and rate limiting
- **Resource Management**: Singleton pattern for shared resources

#### 4. **Increased Flexibility**
- **Strategy Pattern**: Easy to switch between different implementations
- **Factory Pattern**: Dynamic service creation based on configuration
- **Adapter Pattern**: Simplified integration with external services

### Trade-offs

#### 1. **Increased Complexity**
- **Learning Curve**: Team needs to understand multiple design patterns
- **Over-engineering Risk**: May be too complex for simple CRUD operations
- **Initial Development Time**: More upfront work for pattern implementation

#### 2. **Performance Considerations**
- **Memory Overhead**: Additional abstraction layers consume more memory
- **Runtime Overhead**: Multiple layers may add latency to simple operations
- **Caching Complexity**: Cache invalidation strategies become critical

#### 3. **Development Trade-offs**
- **Code Volume**: More files and classes to maintain
- **Debugging Complexity**: More layers to trace through for issues
- **Team Coordination**: Requires consistent pattern usage across team

---

## Testing Strategy

### 1. Unit Testing with Patterns

```python
# tests/test_expense_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.enhanced_expense_service import EnhancedExpenseService
from app.core.unit_of_work import AbstractUnitOfWork
from app.schemas.expenses import ExpenseCreate
import uuid

class TestEnhancedExpenseService:
    
    @pytest.fixture
    def mock_uow(self):
        uow = Mock(spec=AbstractUnitOfWork)
        uow.expenses = Mock()
        uow.commit = Mock()
        uow.rollback = Mock()
        return uow
    
    @pytest.fixture
    def expense_service(self, mock_uow):
        return EnhancedExpenseService(mock_uow)
    
    def test_create_expense_success(self, expense_service, mock_uow):
        # Arrange
        expense_data = ExpenseCreate(
            amount=100.0,
            category="food",
            description="Lunch"
        )
        user_id = uuid.uuid4()
        mock_expense = Mock()
        mock_expense.id = uuid.uuid4()
        mock_uow.expenses.create.return_value = mock_expense
        
        # Act
        result = expense_service.create_expense(expense_data, user_id)
        
        # Assert
        assert result["success"] is True
        assert result["data"] == mock_expense
        mock_uow.expenses.create.assert_called_once()
        mock_uow.commit.assert_called_once()
    
    def test_get_expenses_with_caching(self, expense_service, mock_uow):
        # Test caching behavior
        user_id = uuid.uuid4()
        mock_expenses = [Mock(), Mock()]
        mock_uow.expenses.get_all.return_value = mock_expenses
        mock_uow.expenses.count.return_value = 2
        
        # First call
        result1 = expense_service.get_expenses(user_id)
        # Second call (should use cache)
        result2 = expense_service.get_expenses(user_id)
        
        assert result1 == result2
        # Should only call repository once due to caching
        assert mock_uow.expenses.get_all.call_count == 1

# tests/test_repository.py
import pytest
from sqlalchemy.orm import Session
from app.repositories.expense_repository import ExpenseRepository
from app.models.models import Expense
import uuid

class TestExpenseRepository:
    
    @pytest.fixture
    def expense_repository(self, db_session: Session):
        return ExpenseRepository(db_session, Expense)
    
    def test_create_expense(self, expense_repository, db_session):
        # Arrange
        expense_data = {
            "amount": 100.0,
            "category": "food",
            "description": "Test expense",
            "user_id": uuid.uuid4()
        }
        
        # Act
        expense = expense_repository.create(expense_data)
        
        # Assert
        assert expense.id is not None
        assert expense.amount == 100.0
        assert expense.category == "food"
    
    def test_get_by_id(self, expense_repository, db_session):
        # Create expense first
        expense_data = {
            "amount": 50.0,
            "category": "transport",
            "user_id": uuid.uuid4()
        }
        created_expense = expense_repository.create(expense_data)
        
        # Retrieve by ID
        retrieved_expense = expense_repository.get_by_id(created_expense.id)
        
        assert retrieved_expense is not None
        assert retrieved_expense.id == created_expense.id
        assert retrieved_expense.amount == 50.0
```

### 2. Integration Testing

```python
# tests/integration/test_expense_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

class TestExpenseAPIIntegration:
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        # Mock authentication headers
        return {"Authorization": "Bearer test-token"}
    
    def test_create_and_retrieve_expense(self, client, auth_headers):
        # Create expense
        expense_data = {
            "amount": 75.0,
            "category": "entertainment",
            "description": "Movie tickets"
        }
        
        create_response = client.post(
            "/v2/expenses/",
            json=expense_data,
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        created_expense = create_response.json()
        expense_id = created_expense["data"]["id"]
        
        # Retrieve expenses
        get_response = client.get(
            "/v2/expenses/",
            headers=auth_headers
        )
        
        assert get_response.status_code == 200
        expenses = get_response.json()
        assert len(expenses["data"]) > 0
        
        # Find created expense
        found_expense = next(
            (e for e in expenses["data"] if e["id"] == expense_id),
            None
        )
        assert found_expense is not None
        assert found_expense["amount"] == 75.0
    
    def test_undo_functionality(self, client, auth_headers):
        # Create expense
        expense_data = {
            "amount": 25.0,
            "category": "food",
            "description": "Coffee"
        }
        
        create_response = client.post(
            "/v2/expenses/",
            json=expense_data,
            headers=auth_headers
        )
        assert create_response.status_code == 201
        
        # Undo the creation
        undo_response = client.post(
            "/v2/expenses/undo",
            headers=auth_headers
        )
        assert undo_response.status_code == 200
        
        # Verify expense is removed (implementation dependent)
        # This would require more sophisticated testing setup
```

### 3. Performance Testing

```python
# tests/performance/test_caching_performance.py
import pytest
import time
from app.decorators.caching import cache_result

class TestCachingPerformance:
    
    @cache_result(expiration=60)
    def expensive_operation(self, data):
        # Simulate expensive operation
        time.sleep(0.1)
        return f"processed_{data}"
    
    def test_cache_performance_improvement(self):
        # First call (should be slow)
        start_time = time.time()
        result1 = self.expensive_operation("test_data")
        first_call_time = time.time() - start_time
        
        # Second call (should be fast due to caching)
        start_time = time.time()
        result2 = self.expensive_operation("test_data")
        second_call_time = time.time() - start_time
        
        assert result1 == result2
        assert second_call_time < first_call_time * 0.1  # Should be much faster
```

---

## Migration Path

### Phase 1: Foundation (Week 1-2)
1. **Set up base patterns**: Repository interfaces, UoW, Factory patterns
2. **Create singleton managers**: Configuration, Cache, Logger
3. **Implement basic decorators**: Logging, rate limiting
4. **Update dependency injection**: New service factories

### Phase 2: Core Refactoring (Week 3-4)
1. **Migrate one service**: Start with expense service as example
2. **Implement repository pattern**: For expenses first
3. **Add command pattern**: For expense CRUD operations
4. **Set up observers**: For expense events

### Phase 3: Expansion (Week 5-6)
1. **Migrate remaining services**: Tasks, events, journal, user profile
2. **Implement strategy patterns**: Authentication, AI services
3. **Add advanced decorators**: Caching, validation
4. **Set up comprehensive testing**: Unit and integration tests

### Phase 4: Optimization (Week 7-8)
1. **Performance tuning**: Cache optimization, query optimization
2. **Advanced patterns**: Template methods, adapters
3. **Documentation**: API documentation, pattern documentation
4. **Code review and refinement**: Team review, pattern consistency

---

## Conclusion

This refactoring plan introduces essential design patterns that will transform your FastAPI application into a more maintainable, scalable, and robust system. The patterns work together to create a clean architecture that supports:

- **Easy testing and mocking**
- **Flexible service implementations**
- **Consistent error handling**
- **Performance optimization**
- **Future extensibility**

Start with Phase 1 to establish the foundation, then progressively implement the more advanced patterns. Each phase builds upon the previous one, ensuring a smooth transition while maintaining system stability.

The investment in design patterns will pay dividends in terms of code quality, team productivity, and system maintainability as your application grows and evolves.