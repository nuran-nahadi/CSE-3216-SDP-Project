"""
Database migration script to add Events table
This script should be run after updating the models to add the events functionality
"""

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.models.models import Base, Event


def run_events_migration():
    """Run database migration to add Events table"""
    
    DATABASE_URL = f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_hostname}:{settings.db_port}/{settings.db_name}"
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Start transaction
        trans = connection.begin()
        
        try:
            print("Starting Events table migration...")
            
            # Create events table using SQLAlchemy
            print("Creating Events table...")
            Base.metadata.create_all(engine, tables=[Event.__table__])
            
            # Commit transaction
            trans.commit()
            print("Events migration completed successfully!")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"Events migration failed: {str(e)}")
            raise


if __name__ == "__main__":
    run_events_migration()
