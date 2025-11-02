from typing import Dict, Any, Optional
import logging
from app.core.patterns.singleton import Singleton
from app.core.config_manager import config_manager
from app.core.database_manager import db_manager


class ServiceManager(Singleton):
    """
    Singleton Service Manager.
    
    This class provides centralized access to all application services and managers.
    It acts as a service locator pattern implementation, making it easy to access
    any service from anywhere in the application.
    """
    
    def _setup(self):
        """Initialize the service manager."""
        self._services: Dict[str, Any] = {}
        self._logger = logging.getLogger(__name__)
        self._register_core_services()
    
    def _register_core_services(self):
        """Register core application services."""
        self.register_service("config", config_manager)
        self.register_service("database", db_manager)
        self._logger.info("Core services registered successfully")
    
    def register_service(self, name: str, service: Any):
        """
        Register a service with the service manager.
        
        Args:
            name: The name to register the service under
            service: The service instance to register
        """
        self._services[name] = service
        self._logger.debug(f"Service '{name}' registered")
    
    def get_service(self, name: str) -> Optional[Any]:
        """
        Get a registered service by name.
        
        Args:
            name: The name of the service to retrieve
            
        Returns:
            The service instance, or None if not found
        """
        return self._services.get(name)
    
    def has_service(self, name: str) -> bool:
        """
        Check if a service is registered.
        
        Args:
            name: The name of the service to check
            
        Returns:
            True if the service is registered, False otherwise
        """
        return name in self._services
    
    def unregister_service(self, name: str) -> bool:
        """
        Unregister a service.
        
        Args:
            name: The name of the service to unregister
            
        Returns:
            True if the service was unregistered, False if it wasn't found
        """
        if name in self._services:
            del self._services[name]
            self._logger.debug(f"Service '{name}' unregistered")
            return True
        return False
    
    def list_services(self) -> list:
        """
        Get a list of all registered service names.
        
        Returns:
            List of service names
        """
        return list(self._services.keys())
    
    def get_config_manager(self):
        """Get the configuration manager."""
        return self.get_service("config")
    
    def get_database_manager(self):
        """Get the database manager."""
        return self.get_service("database")
    
    def get_application_status(self) -> dict:
        """
        Get the overall application status.
        
        Returns:
            Dictionary containing status information for all services
        """
        config_mgr = self.get_config_manager()
        db_mgr = self.get_database_manager()
        
        return {
            "services_registered": len(self._services),
            "service_names": self.list_services(),
            "config_status": {
                "debug_mode": config_mgr.is_debug_mode(),
                "auth_disabled": config_mgr.is_auth_disabled()
            },
            "database_status": db_mgr.get_connection_info(),
            "application_healthy": db_mgr.check_connection()
        }
    
    def shutdown(self):
        """Shutdown all services gracefully."""
        self._logger.info("Shutting down all services...")
        
        # Close database connections
        db_mgr = self.get_database_manager()
        if db_mgr:
            db_mgr.close_connections()
        
        # Clear services
        self._services.clear()
        self._logger.info("All services shut down successfully")


# Create the global service manager instance
service_manager = ServiceManager.get_instance()