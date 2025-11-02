from typing import Optional
import os
import logging
from pydantic_settings import BaseSettings
from app.core.patterns.singleton import Singleton


class Settings(BaseSettings):
    """Application settings using Pydantic BaseSettings."""
    
    # Database Configuration
    db_username: str
    db_password: str
    db_hostname: str
    db_port: int = 5432
    db_name: str

    # Supabase Configuration
    supabase_db_url: Optional[str] = None
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None

    # JWT Configuration
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Server Configuration
    local_url: str = "http://localhost:8000"
    ngrok_url: Optional[str] = None
    use_ngrok: bool = False

    # Cloudinary Configuration
    cloudinary_cloud_name: Optional[str] = None
    cloudinary_api_key: Optional[str] = None
    cloudinary_api_secret: Optional[str] = None

    # AI/ML Configuration (Optional)
    google_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # Email Configuration (Optional)
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: Optional[str] = None

    # Development Settings
    debug: bool = False
    log_level: str = "INFO"
    disable_auth: bool = False

    @property
    def database_url(self) -> str:
        """Build database URL from components or use Supabase URL"""
        if self.supabase_db_url:
            return self.supabase_db_url
        return f"postgresql://{self.db_username}:{self.db_password}@{self.db_hostname}:{self.db_port}/{self.db_name}"

    class Config:
        env_file = ".env"
        extra = "forbid"


class ConfigManager(Singleton):
    """
    Singleton Configuration Manager.
    
    This class manages all application configuration settings and provides
    a centralized way to access them throughout the application.
    """
    
    def _setup(self):
        """Initialize the configuration manager."""
        self._settings: Optional[Settings] = None
        self._logger = logging.getLogger(__name__)
        self._load_settings()
    
    def _load_settings(self):
        """Load settings from environment variables and .env file."""
        try:
            self._settings = Settings()
            self._logger.info(f"Configuration loaded successfully. Debug mode: {self._settings.debug}")
        except Exception as e:
            self._logger.error(f"Failed to load configuration: {e}")
            raise
    
    @property
    def settings(self) -> Settings:
        """Get the application settings."""
        if self._settings is None:
            self._load_settings()
        return self._settings
    
    def reload_settings(self):
        """Reload settings from environment variables and .env file."""
        self._logger.info("Reloading configuration settings...")
        self._load_settings()
    
    def get_database_url(self) -> str:
        """Get the database URL."""
        return self.settings.database_url
    
    def is_debug_mode(self) -> bool:
        """Check if the application is in debug mode."""
        return self.settings.debug
    
    def is_auth_disabled(self) -> bool:
        """Check if authentication is disabled."""
        return self.settings.disable_auth
    
    def get_jwt_settings(self) -> dict:
        """Get JWT configuration settings."""
        return {
            "secret_key": self.settings.secret_key,
            "algorithm": self.settings.algorithm,
            "access_token_expire_minutes": self.settings.access_token_expire_minutes,
            "refresh_token_expire_days": self.settings.refresh_token_expire_days
        }
    
    def get_cloudinary_settings(self) -> dict:
        """Get Cloudinary configuration settings."""
        return {
            "cloud_name": self.settings.cloudinary_cloud_name,
            "api_key": self.settings.cloudinary_api_key,
            "api_secret": self.settings.cloudinary_api_secret
        }
    
    def get_ai_settings(self) -> dict:
        """Get AI/ML configuration settings."""
        return {
            "google_api_key": self.settings.google_api_key,
            "openai_api_key": self.settings.openai_api_key
        }
    
    def get_email_settings(self) -> dict:
        """Get email configuration settings."""
        return {
            "smtp_host": self.settings.smtp_host,
            "smtp_port": self.settings.smtp_port,
            "smtp_username": self.settings.smtp_username,
            "smtp_password": self.settings.smtp_password,
            "email_from": self.settings.email_from
        }
    
    def get_server_settings(self) -> dict:
        """Get server configuration settings."""
        return {
            "local_url": self.settings.local_url,
            "ngrok_url": self.settings.ngrok_url,
            "use_ngrok": self.settings.use_ngrok
        }


# Create the global config manager instance
config_manager = ConfigManager.get_instance()

# For backward compatibility, expose settings directly
settings = config_manager.settings