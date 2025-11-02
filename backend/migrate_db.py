"""
Database migration script to update User model and add UserPreferences table
This script should be run after updating the models to ensure database compatibility
"""

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.models.models import Base


def run_migration():
    """Run database migration to update User model and add UserPreferences"""
    
    DATABASE_URL = f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_hostname}:{settings.db_port}/{settings.db_name}"
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Start transaction
        trans = connection.begin()
        
        try:
            print("Starting database migration...")
            
            # Add new columns to users table if they don't exist
            migration_queries = [
                # Add UUID extension for PostgreSQL
                "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",
                
                # Add new columns to users table (if they don't exist)
                """
                DO $$ 
                BEGIN 
                    BEGIN
                        ALTER TABLE users ADD COLUMN first_name VARCHAR;
                    EXCEPTION
                        WHEN duplicate_column THEN RAISE NOTICE 'column first_name already exists in users.';
                    END;
                    
                    BEGIN
                        ALTER TABLE users ADD COLUMN last_name VARCHAR;
                    EXCEPTION
                        WHEN duplicate_column THEN RAISE NOTICE 'column last_name already exists in users.';
                    END;
                    
                    BEGIN
                        ALTER TABLE users ADD COLUMN hashed_password VARCHAR;
                    EXCEPTION
                        WHEN duplicate_column THEN RAISE NOTICE 'column hashed_password already exists in users.';
                    END;
                    
                    BEGIN
                        ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE;
                    EXCEPTION
                        WHEN duplicate_column THEN RAISE NOTICE 'column is_verified already exists in users.';
                    END;
                    
                    BEGIN
                        ALTER TABLE users ADD COLUMN profile_picture_url VARCHAR;
                    EXCEPTION
                        WHEN duplicate_column THEN RAISE NOTICE 'column profile_picture_url already exists in users.';
                    END;
                    
                    BEGIN
                        ALTER TABLE users ADD COLUMN timezone VARCHAR DEFAULT 'UTC';
                    EXCEPTION
                        WHEN duplicate_column THEN RAISE NOTICE 'column timezone already exists in users.';
                    END;
                    
                    BEGIN
                        ALTER TABLE users ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
                    EXCEPTION
                        WHEN duplicate_column THEN RAISE NOTICE 'column updated_at already exists in users.';
                    END;
                END $$;
                """,
                
                # Update existing data - split full_name into first_name and last_name
                """
                UPDATE users 
                SET 
                    first_name = CASE 
                        WHEN position(' ' in full_name) > 0 
                        THEN left(full_name, position(' ' in full_name) - 1)
                        ELSE full_name
                    END,
                    last_name = CASE 
                        WHEN position(' ' in full_name) > 0 
                        THEN right(full_name, length(full_name) - position(' ' in full_name))
                        ELSE ''
                    END,
                    hashed_password = password
                WHERE first_name IS NULL OR last_name IS NULL OR hashed_password IS NULL;
                """,
            ]
            
            # Execute migration queries
            for query in migration_queries:
                print(f"Executing: {query[:100]}...")
                connection.execute(text(query))
            
            # Create UserPreferences table using SQLAlchemy
            print("Creating UserPreferences table...")
            Base.metadata.create_all(engine)
            
            # Commit transaction
            trans.commit()
            print("Migration completed successfully!")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"Migration failed: {str(e)}")
            raise


if __name__ == "__main__":
    run_migration()
