"""
Database migration script to add Tasks table
This script should be run to add the tasks functionality to the database
"""

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.models.models import Base


def run_tasks_migration():
    """Run database migration to add Tasks table"""
    
    DATABASE_URL = f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_hostname}:{settings.db_port}/{settings.db_name}"
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Start transaction
        trans = connection.begin()
        
        try:
            print("Starting tasks table migration...")
            
            # Create custom types if they don't exist
            migration_queries = [
                # Create task priority enum type
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'task_priorities') THEN
                        CREATE TYPE task_priorities AS ENUM ('low', 'medium', 'high');
                    END IF;
                END $$;
                """,
                
                # Create task status enum type
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'task_statuses') THEN
                        CREATE TYPE task_statuses AS ENUM ('pending', 'in_progress', 'completed', 'cancelled');
                    END IF;
                END $$;
                """,
                
                # Create tasks table
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    title VARCHAR NOT NULL,
                    description TEXT,
                    due_date TIMESTAMP WITH TIME ZONE,
                    priority task_priorities NOT NULL DEFAULT 'medium',
                    status task_statuses NOT NULL DEFAULT 'pending',
                    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
                    completion_date TIMESTAMP WITH TIME ZONE,
                    estimated_duration INTEGER,
                    actual_duration INTEGER,
                    tags VARCHAR,
                    parent_task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                );
                """,
                
                # Create indexes for better performance
                """
                CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
                CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
                CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
                CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
                CREATE INDEX IF NOT EXISTS idx_tasks_parent_task_id ON tasks(parent_task_id);
                CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);
                """,
                
                # Create trigger to automatically update updated_at column
                """
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = NOW();
                    RETURN NEW;
                END;
                $$ language 'plpgsql';
                """,
                
                """
                DROP TRIGGER IF EXISTS update_tasks_updated_at ON tasks;
                CREATE TRIGGER update_tasks_updated_at
                    BEFORE UPDATE ON tasks
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column();
                """,
            ]
            
            # Execute migration queries
            for query in migration_queries:
                print(f"Executing: {query.strip()[:100]}...")
                connection.execute(text(query))
            
            # Commit transaction
            trans.commit()
            print("Tasks migration completed successfully!")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"Tasks migration failed: {str(e)}")
            raise


if __name__ == "__main__":
    run_tasks_migration()
