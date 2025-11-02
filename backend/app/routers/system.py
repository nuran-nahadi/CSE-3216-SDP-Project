"""
Example router demonstrating the use of singleton pattern with FastAPI dependencies.

This file shows how to use the new singleton-based dependencies in your routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import (
    get_database_session,
    get_config_manager,
    get_service_manager,
    get_settings
)
from app.core.config_manager import ConfigManager
from app.core.service_manager import ServiceManager

router = APIRouter(
    prefix="/system",
    tags=["System Management"],
    responses={404: {"description": "Not found"}},
)


@router.get("/status")
def get_system_status(
    service_mgr: ServiceManager = Depends(get_service_manager),
    config_mgr: ConfigManager = Depends(get_config_manager)
):
    """
    Get comprehensive system status using singleton managers.
    
    This endpoint demonstrates how to use the singleton pattern
    to access various system managers and their status.
    """
    return {
        "application_status": service_mgr.get_application_status(),
        "config_info": {
            "debug_mode": config_mgr.is_debug_mode(),
            "auth_disabled": config_mgr.is_auth_disabled(),
            "jwt_settings_available": bool(config_mgr.get_jwt_settings().get("secret_key")),
            "database_url_configured": bool(config_mgr.get_database_url())
        },
        "available_services": service_mgr.list_services()
    }


@router.get("/database/info")
def get_database_info(
    db: Session = Depends(get_database_session),
    service_mgr: ServiceManager = Depends(get_service_manager)
):
    """
    Get database connection information.
    
    This endpoint shows how to use the database session dependency
    and access database manager through the service manager.
    """
    db_manager = service_mgr.get_database_manager()
    
    return {
        "connection_info": db_manager.get_connection_info(),
        "connection_healthy": db_manager.check_connection(),
        "session_active": db is not None
    }


@router.get("/config/settings")
def get_config_settings(
    settings = Depends(get_settings)
):
    """
    Get application configuration settings (safe subset).
    
    This endpoint demonstrates how to access configuration settings
    using the dependency injection pattern.
    """
    return {
        "server": {
            "debug": settings.debug,
            "log_level": settings.log_level,
            "local_url": settings.local_url,
            "use_ngrok": settings.use_ngrok
        },
        "database": {
            "hostname": settings.db_hostname,
            "port": settings.db_port,
            "name": settings.db_name,
            "has_supabase_url": bool(settings.supabase_db_url)
        },
        "auth": {
            "algorithm": settings.algorithm,
            "access_token_expire_minutes": settings.access_token_expire_minutes,
            "refresh_token_expire_days": settings.refresh_token_expire_days,
            "disabled": settings.disable_auth
        },
        "features": {
            "has_cloudinary": bool(settings.cloudinary_cloud_name),
            "has_ai_keys": bool(settings.google_api_key or settings.openai_api_key),
            "has_email_config": bool(settings.smtp_host)
        }
    }


@router.post("/config/reload")
def reload_configuration(
    config_mgr: ConfigManager = Depends(get_config_manager)
):
    """
    Reload application configuration.
    
    This endpoint demonstrates how to use singleton methods
    to reload configuration without restarting the application.
    """
    try:
        config_mgr.reload_settings()
        return {
            "success": True,
            "message": "Configuration reloaded successfully",
            "debug_mode": config_mgr.is_debug_mode()
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to reload configuration: {str(e)}"
        }


@router.post("/database/reset")
def reset_database_connection(
    service_mgr: ServiceManager = Depends(get_service_manager)
):
    """
    Reset database connection.
    
    This endpoint demonstrates how to use singleton methods
    to reset database connections without restarting the application.
    """
    try:
        db_manager = service_mgr.get_database_manager()
        db_manager.reset_connection()
        
        return {
            "success": True,
            "message": "Database connection reset successfully",
            "connection_info": db_manager.get_connection_info()
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to reset database connection: {str(e)}"
        }