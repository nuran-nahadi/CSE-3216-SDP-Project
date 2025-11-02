# This file is kept for backward compatibility
# New database management is handled by DatabaseManager singleton
# Import the new database manager for access to database connections

from app.core.database_manager import db_manager, get_db, Base, engine

# For backward compatibility, expose the database objects directly
SessionLocal = db_manager.session_factory

__all__ = ["get_db", "Base", "engine", "SessionLocal", "db_manager"]
