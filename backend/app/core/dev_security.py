from app.models.models import User
from sqlalchemy.orm import Session
from fastapi import Depends
from app.core.database_manager import db_manager
from uuid import UUID


def get_development_user(db: Session = Depends(db_manager.get_db)) -> User:
    """
    Get a default user for development purposes.
    This bypasses all authentication and returns the first user in the database.
    """
    # Try to get the test user with the fixed UUID from tables.sql
    user = db.query(User).filter(User.id == UUID('11111111-1111-1111-1111-111111111111')).first()
    
    # If test user doesn't exist, get any user
    if not user:
        user = db.query(User).first()
    
    # If no users exist at all, create a default one
    if not user:
        from app.core.security import get_password_hash
        user = User(
            username="dev_user",
            email="dev@example.com",
            first_name="Dev",
            last_name="User",
            hashed_password=get_password_hash("password"),
            is_verified=True,
            timezone="UTC",
            role="user",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user


def disable_admin_check():
    """Mock function that allows all requests to pass admin checks"""
    pass