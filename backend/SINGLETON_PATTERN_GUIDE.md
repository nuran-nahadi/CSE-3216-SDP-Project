# Singleton Pattern Implementation for FastAPI Backend

This document describes the singleton pattern implementation for database and configuration management in the FastAPI backend.

## Overview

The singleton pattern ensures that only one instance of a class exists throughout the application lifecycle. This is particularly useful for:

- **Database Management**: Single connection pool and session management
- **Configuration Management**: Centralized configuration access and updates
- **Service Management**: Centralized service location and management

## Architecture

### Core Components

1. **Singleton Base Class** (`app/core/patterns/singleton.py`)
   - Thread-safe singleton metaclass
   - Abstract base class for singleton implementations
   - Automatic instance management

2. **Configuration Manager** (`app/core/config_manager.py`)
   - Singleton for managing application configuration
   - Environment variable handling
   - Configuration validation and access methods

3. **Database Manager** (`app/core/database_manager.py`)
   - Singleton for database connection management
   - Connection pooling and session handling
   - Health checks and connection monitoring

4. **Service Manager** (`app/core/service_manager.py`)
   - Service locator pattern implementation
   - Centralized access to all application services
   - Application status monitoring

5. **Dependencies** (`app/core/dependencies.py`)
   - FastAPI dependency injection functions
   - Singleton-aware dependency providers
   - Backward compatibility support

## Usage Examples

### Basic Singleton Usage

```python
from app.core.config_manager import config_manager
from app.core.database_manager import db_manager

# Get configuration settings
settings = config_manager.settings
debug_mode = config_manager.is_debug_mode()

# Get database session
with db_manager.get_db_context() as db:
    # Use database session
    pass
```

### FastAPI Route Dependencies

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_database_session, get_config_manager

router = APIRouter()

@router.get("/example")
def example_endpoint(
    db: Session = Depends(get_database_session),
    config_mgr = Depends(get_config_manager)
):
    # Use injected dependencies
    return {"debug": config_mgr.is_debug_mode()}
```

### Service Manager Usage

```python
from app.core.service_manager import service_manager

# Get application status
status = service_manager.get_application_status()

# Access specific services
config_mgr = service_manager.get_config_manager()
db_mgr = service_manager.get_database_manager()
```

## Benefits

### 1. Resource Management
- Single database connection pool
- Reduced memory footprint
- Better connection handling

### 2. Configuration Management
- Centralized configuration access
- Runtime configuration updates
- Environment-specific settings

### 3. Consistency
- Single source of truth for services
- Consistent behavior across the application
- Easier testing and mocking

### 4. Performance
- Reduced object creation overhead
- Efficient resource utilization
- Better connection pooling

## Thread Safety

All singleton implementations are thread-safe using:
- Thread locks for instance creation
- Proper synchronization mechanisms
- Safe initialization patterns

## Backward Compatibility

The implementation maintains backward compatibility:
- Existing imports continue to work
- Previous dependency patterns are supported
- Gradual migration path available

## Migration Guide

### For Existing Code

1. **Database Dependencies**: No changes needed, existing `get_db()` continues to work
2. **Configuration Access**: Existing `settings` import continues to work
3. **New Features**: Use new dependency functions for enhanced functionality

### Recommended Updates

```python
# Old way
from app.db.database import get_db
from app.core.config import settings

# New way (recommended)
from app.core.dependencies import get_database_session, get_settings
```

## Configuration

The singleton pattern works with existing configuration:
- `.env` files
- Environment variables
- Pydantic settings validation

## Monitoring and Health Checks

### System Status Endpoint
- `/system/status` - Overall application status
- `/system/database/info` - Database connection status
- `/system/config/settings` - Configuration overview

### Health Monitoring
```python
# Check database health
healthy = db_manager.check_connection()

# Get connection pool status
info = db_manager.get_connection_info()

# Monitor application status
status = service_manager.get_application_status()
```

## Best Practices

### 1. Dependency Injection
- Use FastAPI dependencies for service access
- Avoid direct singleton access in routes
- Leverage type hints for better IDE support

### 2. Error Handling
- Handle initialization failures gracefully
- Implement retry mechanisms for connections
- Log singleton lifecycle events

### 3. Testing
- Use singleton reset methods for testing
- Mock dependencies appropriately
- Test singleton behavior in isolation

### 4. Service Registration
```python
# Register custom services
service_manager.register_service("custom_service", my_service)

# Access registered services
my_service = service_manager.get_service("custom_service")
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all modules are properly imported
2. **Circular Dependencies**: Use dependency injection to avoid circular imports
3. **Connection Issues**: Check database configuration and connectivity
4. **Configuration Errors**: Validate environment variables and .env files

### Debug Information

```python
# Get debug information
status = service_manager.get_application_status()
config_info = config_manager.settings
db_info = db_manager.get_connection_info()
```

## Future Enhancements

Potential areas for extension:
- Cache management singleton
- Logging manager singleton
- External service managers
- Event system integration

This singleton implementation provides a solid foundation for scalable and maintainable FastAPI applications with proper resource management and configuration handling.