"""
FastAPI Dependencies with Singleton Pattern Integration

This module provides FastAPI dependency functions that integrate with our singleton pattern.
These dependencies can be used in FastAPI route handlers to inject the required services.
"""

from typing import Iterator

from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.service_manager import service_manager
from app.core.config_manager import config_manager
from app.core.database_manager import db_manager
from app.core.config import settings
from app.core.security import get_current_authenticated_user, check_admin_role
from app.core.dev_security import get_development_user, disable_admin_check
from app.repositories.expense_repository import ExpenseRepository


def get_service_manager():
    """
    FastAPI dependency to get the service manager.
    
    Returns:
        The singleton service manager instance
    """
    return service_manager


def get_config_manager():
    """
    FastAPI dependency to get the configuration manager.
    
    Returns:
        The singleton configuration manager instance
    """
    return config_manager


def get_database_manager():
    """
    FastAPI dependency to get the database manager.
    
    Returns:
        The singleton database manager instance
    """
    return db_manager


def get_database_session() -> Session:
    """
    FastAPI dependency to get a database session.
    This is the recommended way to get database sessions in FastAPI routes.
    
    Yields:
        A database session that will be automatically closed
    """
    yield from db_manager.get_db()


def get_expense_repository(db: Session = Depends(get_database_session)) -> Iterator[ExpenseRepository]:
    """Provide an expense repository bound to the current database session."""
    yield ExpenseRepository(db)


def get_settings():
    """
    FastAPI dependency to get application settings.
    
    Returns:
        The application settings object
    """
    return config_manager.settings


def get_jwt_settings():
    """
    FastAPI dependency to get JWT settings.
    
    Returns:
        Dictionary containing JWT configuration
    """
    return config_manager.get_jwt_settings()


def get_cloudinary_settings():
    """
    FastAPI dependency to get Cloudinary settings.
    
    Returns:
        Dictionary containing Cloudinary configuration
    """
    return config_manager.get_cloudinary_settings()


def get_ai_settings():
    """
    FastAPI dependency to get AI/ML settings.
    
    Returns:
        Dictionary containing AI/ML configuration
    """
    return config_manager.get_ai_settings()


def get_email_settings():
    """
    FastAPI dependency to get email settings.
    
    Returns:
        Dictionary containing email configuration
    """
    return config_manager.get_email_settings()


def get_server_settings():
    """
    FastAPI dependency to get server settings.
    
    Returns:
        Dictionary containing server configuration
    """
    return config_manager.get_server_settings()


# For backward compatibility with existing code
def get_db() -> Session:
    """
    Backward compatibility function for getting database sessions.
    
    Yields:
        A database session that will be automatically closed
    """
    yield from db_manager.get_db()


# Authentication dependencies (existing)
def get_current_user():
    """
    Returns the appropriate user dependency based on auth settings
    """
    if settings.disable_auth:
        return get_development_user
    else:
        return get_current_authenticated_user


def get_admin_check():
    """
    Returns the appropriate admin check dependency based on auth settings
    """
    if settings.disable_auth:
        return disable_admin_check
    else:
        return check_admin_role