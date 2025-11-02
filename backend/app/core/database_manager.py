from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator, Optional
import logging
from contextlib import contextmanager
from app.core.patterns.singleton import Singleton
from app.core.config_manager import config_manager


class DatabaseManager(Singleton):
    """
    Singleton Database Manager.
    
    This class manages the database connection, engine, and session handling
    for the entire application. It ensures that only one database connection
    pool exists throughout the application lifecycle.
    """
    
    def _setup(self):
        """Initialize the database manager."""
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        self._base = declarative_base()
        self._logger = logging.getLogger(__name__)
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the database engine and session factory."""
        try:
            database_url = config_manager.get_database_url()
            self._logger.info(f"Initializing database connection to: {database_url.split('@')[0]}@***")
            
            # Create engine with connection pooling and SSL settings for Supabase
            self._engine = create_engine(
                database_url,
                pool_pre_ping=True,      # Verify connections before use
                pool_recycle=300,        # Recycle connections every 5 minutes
                pool_size=10,            # Number of connections to maintain
                max_overflow=20,         # Maximum overflow connections
                connect_args={
                    "sslmode": "require",     # Require SSL for Supabase
                    "connect_timeout": 10     # Connection timeout
                } if "supabase" in database_url else {}
            )
            
            # Create session factory
            self._session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )
            
            # Create all tables
            self._base.metadata.create_all(self._engine)
            
            self._logger.info("Database initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize database: {e}")
            raise
    
    @property
    def engine(self) -> Engine:
        """Get the database engine."""
        if self._engine is None:
            self._initialize_database()
        return self._engine
    
    @property
    def base(self):
        """Get the declarative base for models."""
        return self._base
    
    @property
    def session_factory(self) -> sessionmaker:
        """Get the session factory."""
        if self._session_factory is None:
            self._initialize_database()
        return self._session_factory
    
    def get_session(self) -> Session:
        """
        Create a new database session.
        
        Returns:
            A new SQLAlchemy session instance.
        """
        return self.session_factory()
    
    def get_db(self) -> Generator[Session, None, None]:
        """
        FastAPI dependency function to get a database session.
        
        Yields:
            A database session that will be automatically closed.
        """
        session = self.get_session()
        try:
            yield session
        finally:
            session.close()
    
    @contextmanager
    def get_db_context(self):
        """
        Context manager for database sessions.
        
        Usage:
            with db_manager.get_db_context() as db:
                # Use db session here
                pass
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_tables(self):
        """Create all database tables."""
        self._base.metadata.create_all(self._engine)
        self._logger.info("Database tables created")
    
    def drop_tables(self):
        """Drop all database tables. Use with caution!"""
        self._base.metadata.drop_all(self._engine)
        self._logger.warning("All database tables dropped")
    
    def check_connection(self) -> bool:
        """
        Check if the database connection is healthy.
        
        Returns:
            True if connection is healthy, False otherwise.
        """
        try:
            with self.engine.connect() as connection:
                from sqlalchemy import text
                connection.execute(text("SELECT 1"))
            return True
        except Exception as e:
            self._logger.error(f"Database connection check failed: {e}")
            return False
    
    def get_connection_info(self) -> dict:
        """
        Get database connection information.
        
        Returns:
            Dictionary containing connection details.
        """
        if self._engine is None:
            return {"status": "not_initialized"}
        
        return {
            "status": "initialized",
            "pool_size": self._engine.pool.size(),
            "checked_out_connections": self._engine.pool.checkedout(),
            "checked_in_connections": self._engine.pool.checkedin(),
            "is_healthy": self.check_connection()
        }
    
    def close_connections(self):
        """Close all database connections."""
        if self._engine:
            self._engine.dispose()
            self._logger.info("Database connections closed")
    
    def reset_connection(self):
        """Reset the database connection."""
        self.close_connections()
        self._engine = None
        self._session_factory = None
        self._initialize_database()
        self._logger.info("Database connection reset")


# Create the global database manager instance
db_manager = DatabaseManager.get_instance()

# For backward compatibility, expose the get_db function and Base
get_db = db_manager.get_db
Base = db_manager.base
engine = db_manager.engine