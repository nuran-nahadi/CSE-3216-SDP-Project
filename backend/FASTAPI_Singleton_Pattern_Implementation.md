# Singleton Pattern Implementation (Backend)

This document explains how the Singleton pattern is implemented and used in the backend, why it was introduced, and what code changes/modifications were made to adopt it. It also shows how to use the provided singletons safely in your code and tests.

## Overview

- Goal: Provide a single, globally accessible instance for configuration, database management, and service discovery with thread-safe initialization.
- Pattern: A reusable, thread-safe Singleton base powered by a custom metaclass that avoids ABC metaclass conflicts.
- Scope: Configuration management, database engine/sessions, and a service locator are implemented as singletons.

## Files and Responsibilities

- `app/core/patterns/singleton.py`
  - Provides the reusable, thread-safe singleton infrastructure via `SingletonMeta`, `SingletonABCMeta`, and the `Singleton` base class.
- `app/core/config_manager.py`
  - `ConfigManager` singleton wraps Pydantic `Settings` and exposes config across the app.
  - Exports a global instance `config_manager` and maintains backward compatibility via `settings` alias.
- `app/core/database_manager.py`
  - `DatabaseManager` singleton owns DB engine creation, session factory, and health checks.
  - Exports a global instance `db_manager` and backward-compat shims: `get_db`, `Base`, `engine`.
- `app/core/service_manager.py`
  - `ServiceManager` singleton acts as a service locator. Registers core services: `config` and `database`.
  - Exports a global `service_manager`.
- `test_singleton_implementation.py`
  - Verifies uniqueness, thread-safety, and basic functionality for all singletons.

## Core Implementation Details

### Thread-safe metaclass: `SingletonMeta`
- Maintains a class-level dictionary `_instances` mapping classes to their singleton instance.
- Guarded by a process-wide `threading.Lock` to ensure only one instance is created, even when multiple threads call the constructor concurrently.
- Overridden `__call__` checks for an existing instance; if none, it creates exactly one under the lock and reuses it afterwards.

### ABC-compatible metaclass: `SingletonABCMeta`
- Inherits from both `SingletonMeta` and `ABCMeta` to resolve metaclass conflicts when building abstract singletons.

### Base class: `Singleton`
- Declared with `metaclass=SingletonABCMeta` so any subclass becomes a thread-safe singleton automatically.
- Idempotent `__init__` guarded by an `_initialized` attribute so initialization runs once per process.
- `_setup()` hook contains the actual one-time initialization logic for subclasses.
- `get_instance()` returns the singleton instance (equivalent to constructing the class).
- `reset()` clears `_initialized` and reruns `_setup()`; intended for testing.

## Concrete Singletons

### 1) ConfigManager (`app/core/config_manager.py`)
- Wraps:
  - `Settings` (Pydantic BaseSettings) that reads environment variables from `.env` (via `env_file = ".env"`).
  - All configuration fields (DB, JWT, Cloudinary, AI, Email, server flags, etc.).
- Responsibilities:
  - Load and expose `settings` safely (`_load_settings()` with logging and error propagation).
  - Provide helpers: `get_database_url()`, `is_debug_mode()`, `is_auth_disabled()`, `get_jwt_settings()`, `get_cloudinary_settings()`, `get_ai_settings()`, `get_email_settings()`, `get_server_settings()`.
  - `reload_settings()` to re-read configuration.
- Globals and compatibility:
  - `config_manager = ConfigManager.get_instance()`
  - `settings = config_manager.settings` (backward compatibility so legacy code importing `settings` still works).

### 2) DatabaseManager (`app/core/database_manager.py`)
- Responsibilities:
  - Initialize SQLAlchemy `Engine` with sensible pooling defaults; enforce SSL for Supabase URLs (`sslmode=require`).
  - Maintain a `sessionmaker` for creating `Session` instances.
  - Provide FastAPI dependency `get_db()` that yields/cleans sessions per request.
  - Context manager `get_db_context()` for imperative usage.
  - Utilities: `create_tables()`, `drop_tables()`, `check_connection()`, `get_connection_info()`, `close_connections()`, `reset_connection()`.
- Globals and compatibility:
  - `db_manager = DatabaseManager.get_instance()`
  - Back-compat exports for legacy import paths: `get_db`, `Base`, `engine` bound to singleton internals.

### 3) ServiceManager (`app/core/service_manager.py`)
- Responsibilities:
  - Central registry for cross-cutting services: `register_service(name, obj)`, `get_service(name)`, `has_service(name)`, `unregister_service(name)`, `list_services()`.
  - Registers core services at startup: `config` -> `config_manager`, `database` -> `db_manager`.
  - `get_application_status()` aggregates health/config flags.
  - `shutdown()` gracefully disposes services (e.g., closes DB connections) and clears registry.
- Globals:
  - `service_manager = ServiceManager.get_instance()`

## Thread Safety and Tests

- `test_singleton_implementation.py` creates instances in parallel using `ThreadPoolExecutor` (10 workers × 20 submissions) and asserts that all instance IDs are identical across threads for each singleton.
- Also validates basic functionality: configuration access, DB engine/session creation, service registration, and backward compatibility imports.

## Usage Examples

### Access configuration
```python
from app.core.config_manager import config_manager

secret = config_manager.get_jwt_settings()["secret_key"]
use_ngrok = config_manager.get_server_settings()["use_ngrok"]
```

### FastAPI endpoint with DB dependency
```python
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from app.core.database_manager import get_db

router = APIRouter()

@router.get("/items")
def list_items(db: Session = Depends(get_db)):
    # use db here
    return {"ok": True}
```

### Use the service locator
```python
from app.core.service_manager import service_manager

config = service_manager.get_config_manager()
database = service_manager.get_database_manager()
```

### Reset singletons in tests (use sparingly)
```python
from app.core.database_manager import db_manager

db_manager.reset_connection()
```

## Changes / Modifications Introduced by the Singleton Refactor

1. Introduced reusable pattern infrastructure
   - New file `app/core/patterns/singleton.py` with `SingletonMeta`, `SingletonABCMeta`, and `Singleton` base.
2. Centralized configuration access
   - New `ConfigManager` singleton (`app/core/config_manager.py`) wraps Pydantic `Settings`.
   - Global `config_manager` for DI/service lookup and `settings` alias for backward compatibility.
3. Centralized database lifecycle management
   - New `DatabaseManager` singleton (`app/core/database_manager.py`) owns engine, sessions, health checks.
   - Global `db_manager` and back-compat re-exports: `get_db`, `Base`, `engine`.
4. Service locator for cross-cutting dependencies
   - New `ServiceManager` singleton (`app/core/service_manager.py`) registers and exposes core services.
5. Thread-safety verification
   - New `test_singleton_implementation.py` verifies uniqueness and thread safety under concurrent access.
6. Backward compatibility shims
   - Continued support for legacy imports (`settings` and `get_db`/`Base`/`engine`) to enable incremental migration of routers and modules.

## Migration Guidance for New Code

- Prefer importing from the new singletons rather than creating new instances or using module-level globals:
  - Configuration: `from app.core.config_manager import config_manager`
  - Database: `from app.core.database_manager import get_db, db_manager`
  - Services: `from app.core.service_manager import service_manager`
- Avoid constructing `Settings()` directly in app code; use `config_manager.settings` or helper methods.
- Avoid creating ad-hoc SQLAlchemy engines/sessions; always use `db_manager` or the `get_db` dependency.

## Pitfalls and Best Practices

- Ensure the `.env` file is present and values are set for required settings (DB credentials, `SECRET_KEY`, etc.).
- Avoid calling `reset()` in production; it is designed for tests.
- When adding new singletons, inherit from `Singleton` and implement `_setup()` for one-time init.
- If you add new cross-cutting services (e.g., cache, message bus), register them in `ServiceManager`.

---

Last updated: 2025-11-02
