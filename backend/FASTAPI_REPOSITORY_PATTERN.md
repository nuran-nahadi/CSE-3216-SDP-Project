# Repository Pattern in the Backend

This document explains what the Repository Pattern is and how it is implemented in this backend. It also shows where it fits in the overall FastAPI architecture of the project and how to extend it safely.

## What is the Repository Pattern?

The Repository Pattern abstracts the data-access layer so the rest of the application (services, API routes, business logic) doesn’t need to know about SQL or how the database is queried. Instead, higher layers depend on repository interfaces or classes that expose clearly named methods such as create, update, or domain-specific queries.

Benefits:
- Separation of concerns: business logic doesn’t contain SQL/ORM details
- Testability: services can be tested by replacing repositories with fakes/mocks
- Consistency: reusable CRUD helpers and query patterns
- Flexibility: switching databases or tuning queries in one place

## Where it fits in this project

High-level flow for expenses:

- Router (`app/routers/expenses.py`) handles HTTP, request/response models, and DI
- Service (`app/services/expenses.py`) implements application/business logic
- Repository (`app/repositories/expense_repository.py`) encapsulates all DB queries
- Session and engine are provided via the database manager singleton (`app/core/database_manager.py`)
- Models (`app/models/models.py`) are SQLAlchemy ORM models used by repositories

ASCII view:

```
[FastAPI Router]
      |
      v
  [ExpenseService]
      |
      v
[ExpenseRepository]
      |
      v
[SQLAlchemy Session] --> [PostgreSQL]
```

## Core building block: BaseRepository

File: `app/repositories/base.py`

- Generic class bound to a SQLAlchemy `Session` and a concrete `model` (ORM mapped class)
- Provides common helpers used by all repositories:
  - `db` (Session) and `model` (ORM class) accessors
  - `refresh(instance)`
  - `commit()` and `rollback()` transaction helpers

This base keeps basic DB operations in one place so concrete repositories focus on domain-specific queries.

## ExpenseRepository: concrete data-access for expenses

File: `app/repositories/expense_repository.py`

Extends `BaseRepository[Expense]` and adds domain-specific queries for the `Expense` model. Key methods:

- Reading and pagination
  - `list_expenses(user_id, start_date, end_date, category, min_amount, max_amount, search, page, limit) -> (items, total)`
  - `list_in_period(user_id, start_date, end_date) -> List[Expense]`
  - `list_for_export(user_id, start_date, end_date) -> List[Expense]`
  - `get_expense_for_user(expense_id, user_id) -> Optional[Expense]`
  - `get_recurring_expenses(user_id) -> List[Expense]`
  - `get_expenses_since(user_id, start_date) -> List[Expense]`

- Mutations
  - `create_expense(user_id, data: ExpenseCreate) -> Expense`
  - `update_expense(expense, update_data: dict) -> Expense`
  - `delete_expense(expense) -> None`
  - `set_receipt_url(expense, receipt_url) -> Expense`

- Aggregations/analytics
  - `get_category_totals(user_id)` and `get_category_totals_in_period(user_id, start_date, end_date)`
  - `get_monthly_expenses(user_id, year, month)`
  - `sum_in_period(user_id, start_date, end_date) -> float`
  - `get_monthly_category_totals(user_id, start_date, end_date)`
  - `get_top_transactions(user_id, start_date, limit)`

- Internal filtering helper
  - `_filtered_query(...)` builds a composable base SQLAlchemy query with optional filters (date range, category, amount range, search across description/merchant/subcategory)

Implementation notes:
- Uses SQLAlchemy expressions (`and_`, `func`, `extract`, ordering, `ilike` for search)
- Serializes/deserializes `tags` to JSON when persisting/reading
- Calls `self.commit()` and `self.refresh()` to persist and materialize the latest state

## Models used by repositories

File: `app/models/models.py`

- SQLAlchemy ORM models: `User`, `UserPreferences`, `Expense`, `Event`, `Task`, `JournalEntry`
- `Expense` captures typical expense data (amount, currency, category, subcategory, merchant, description, date, payment_method, is_recurring, tags, etc.) and references `User`
- All models inherit `Base` from the database manager (see below)

## Session management and dependency injection

Files: 
- `app/core/database_manager.py`
- `app/core/dependencies.py`
- `app/db/database.py` (backward-compat shim)

### DatabaseManager singleton

`DatabaseManager` is implemented as a singleton (`app/core/database_manager.py`) and is the source of truth for:
- SQLAlchemy engine creation and connection pooling (with sensible defaults and Supabase SSL options)
- Declarative base (`Base`) used by ORM models
- Session factory (`sessionmaker`) and request-scoped sessions via `get_db()` generator
- Utilities: `create_tables()`, `drop_tables()`, `check_connection()`, `close_connections()`, `reset_connection()`

Exports:
- `db_manager = DatabaseManager.get_instance()`
- `get_db = db_manager.get_db`
- `Base = db_manager.base`
- `engine = db_manager.engine`

`app/db/database.py` re-exports these for backward compatibility (`Base`, `engine`, `get_db`, `SessionLocal`).

### FastAPI dependencies

`app/core/dependencies.py` provides DI helpers:
- `get_database_session()` yields a SQLAlchemy `Session` using `db_manager.get_db()`
- `get_expense_repository(db=Depends(get_database_session))` yields an `ExpenseRepository` bound to the current session
- Authentication-related dependencies are also provided (`get_current_user()` etc.)

In practice, services often receive the `Session` and instantiate repositories directly (`ExpenseRepository(db)`), which is equivalent to injecting the repository via dependency. Both approaches keep DB details out of routers/controllers.

## Consumption from the service layer

File: `app/services/expenses.py`

The `ExpenseService` is the application/business layer that orchestrates:
- Validating or transforming request data
- Calling repository methods for data access
- Handling errors and rolling back when needed
- Mapping ORM entities to response schemas

Examples:
- `get_expenses(...)` uses `ExpenseRepository.list_expenses(...)` and paginates
- `create_expense(...)` uses `ExpenseRepository.create_expense(...)`; on errors it calls `repo.rollback()` and returns HTTP 500
- Analytics methods (e.g., `get_total_spend_dashboard`, `get_category_breakdown_dashboard`) delegate to repository aggregations and post-process the results for the API

This keeps controllers (routers) thin and free of query logic.

## Exposure via routers

File: `app/routers/expenses.py`

Routers:
- Declare endpoints and response models
- Inject a request-scoped DB session: `db: Session = Depends(get_database_session)`
- Resolve the authenticated user via `get_current_user()`
- Delegate to `ExpenseService` for logic and persistence via repositories

This maintains a clean layering: Router -> Service -> Repository -> DB

## Transactions and error handling

- Most repository methods commit and refresh the entity when they change data
- Services catch exceptions around writes and call `repo.rollback()` before raising an `HTTPException`
- Read-only operations don’t commit

Trade-off: Having repositories call `commit()` is convenient, but if you ever need multi-entity atomic operations across multiple repositories, consider orchestrating the transaction at the service layer (commit once) and let repositories avoid committing themselves. The current design works well for the app’s current use-cases.

## Extending the pattern

To add a repository for a new model (e.g., `Task`):

1) Create the repository file, e.g. `app/repositories/task_repository.py`:

```python
from sqlalchemy.orm import Session
from app.models.models import Task
from app.repositories.base import BaseRepository

class TaskRepository(BaseRepository[Task]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Task)

    # add domain-specific queries here
    # def list_by_user(self, user_id: UUID): ...
```

2) Use it from a service:

```python
repo = TaskRepository(db)
items = repo.db.query(repo.model).filter(repo.model.user_id == user.id).all()
```

3) Optionally add a DI provider in `dependencies.py` similar to `get_expense_repository`.

## Edge cases handled in repositories/services

- `tags` field stored as JSON string in DB; services normalize it to a list in responses
- Search uses `ilike` across `description`, `merchant`, `subcategory`
- Pagination uses `offset`/`limit` and returns `total` for client-side paging
- Date filtering covers inclusive ranges; month/year helpers use SQL `extract`

## Summary

- Repositories encapsulate all SQLAlchemy queries and write operations for a model
- Services contain business logic and compose repository calls
- Routers focus on HTTP IO and dependency injection
- The `DatabaseManager` singleton standardizes engine/session lifecycle and keeps DB configuration in one place

This layering yields clean, testable code that’s easy to evolve as the data-access needs grow.