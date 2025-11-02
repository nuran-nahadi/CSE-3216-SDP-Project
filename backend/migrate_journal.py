"""
Database migration script to add JournalEntry table
This script should be run after updating the models to add journal functionality
"""

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.models.models import Base


def run_migration():
    """Run database migration to add JournalEntry table"""
    
    DATABASE_URL = f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_hostname}:{settings.db_port}/{settings.db_name}"
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Start transaction
        trans = connection.begin()
        
        try:
            print("Starting journal entries migration...")
            
            # Create journal_moods enum type
            create_mood_enum = """
            DO $$ BEGIN
                CREATE TYPE journal_moods AS ENUM (
                    'very_happy', 'happy', 'neutral', 'sad', 'very_sad',
                    'angry', 'excited', 'anxious', 'grateful'
                );
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
            """
            connection.execute(text(create_mood_enum))
            print("✓ Created journal_moods enum type")
            
            # Create journal_entries table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS journal_entries (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(255),
                content TEXT NOT NULL,
                mood journal_moods,
                sentiment_score FLOAT CHECK (sentiment_score >= -1.0 AND sentiment_score <= 1.0),
                keywords TEXT,
                summary TEXT,
                weather VARCHAR(100),
                location VARCHAR(255),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
            );
            """
            connection.execute(text(create_table_query))
            print("✓ Created journal_entries table")
            
            # Create indexes for better performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_journal_entries_user_id ON journal_entries(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_journal_entries_created_at ON journal_entries(created_at);",
                "CREATE INDEX IF NOT EXISTS idx_journal_entries_mood ON journal_entries(mood);",
                "CREATE INDEX IF NOT EXISTS idx_journal_entries_user_created ON journal_entries(user_id, created_at DESC);"
            ]
            
            for index_query in indexes:
                connection.execute(text(index_query))
            print("✓ Created indexes for journal_entries table")
            
            # Create trigger for updated_at column
            trigger_query = """
            CREATE OR REPLACE FUNCTION update_journal_entries_updated_at()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ language 'plpgsql';
            
            DROP TRIGGER IF EXISTS trigger_update_journal_entries_updated_at ON journal_entries;
            CREATE TRIGGER trigger_update_journal_entries_updated_at
                BEFORE UPDATE ON journal_entries
                FOR EACH ROW
                EXECUTE FUNCTION update_journal_entries_updated_at();
            """
            connection.execute(text(trigger_query))
            print("✓ Created trigger for updated_at column")
            
            # Commit transaction
            trans.commit()
            print("✅ Journal entries migration completed successfully!")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"❌ Migration failed: {str(e)}")
            raise e


if __name__ == "__main__":
    run_migration()
