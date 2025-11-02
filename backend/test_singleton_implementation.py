#!/usr/bin/env python3
"""
Test script to verify the singleton pattern implementation.

This script tests:
1. Singleton instance creation and uniqueness
2. Database connection management
3. Configuration management
4. Service manager functionality
5. Thread safety of singleton implementations

Run this script to validate the singleton pattern implementation.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.config_manager import ConfigManager, config_manager
from app.core.database_manager import DatabaseManager, db_manager
from app.core.service_manager import ServiceManager, service_manager


def test_singleton_uniqueness():
    """Test that singletons return the same instance."""
    print("Testing singleton uniqueness...")
    
    # Test ConfigManager
    config1 = ConfigManager.get_instance()
    config2 = ConfigManager()
    config3 = config_manager
    
    assert config1 is config2 is config3, "ConfigManager instances are not the same!"
    print("✓ ConfigManager singleton test passed")
    
    # Test DatabaseManager
    db1 = DatabaseManager.get_instance()
    db2 = DatabaseManager()
    db3 = db_manager
    
    assert db1 is db2 is db3, "DatabaseManager instances are not the same!"
    print("✓ DatabaseManager singleton test passed")
    
    # Test ServiceManager
    service1 = ServiceManager.get_instance()
    service2 = ServiceManager()
    service3 = service_manager
    
    assert service1 is service2 is service3, "ServiceManager instances are not the same!"
    print("✓ ServiceManager singleton test passed")


def test_thread_safety():
    """Test thread safety of singleton implementations."""
    print("\nTesting thread safety...")
    
    instances = {"config": [], "database": [], "service": []}
    
    def create_instances():
        instances["config"].append(ConfigManager.get_instance())
        instances["database"].append(DatabaseManager.get_instance())
        instances["service"].append(ServiceManager.get_instance())
    
    # Create instances from multiple threads
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(create_instances) for _ in range(20)]
        for future in futures:
            future.result()
    
    # Check all instances are the same
    config_set = set(id(instance) for instance in instances["config"])
    database_set = set(id(instance) for instance in instances["database"])
    service_set = set(id(instance) for instance in instances["service"])
    
    assert len(config_set) == 1, f"ConfigManager not thread-safe: {len(config_set)} different instances"
    assert len(database_set) == 1, f"DatabaseManager not thread-safe: {len(database_set)} different instances"
    assert len(service_set) == 1, f"ServiceManager not thread-safe: {len(service_set)} different instances"
    
    print("✓ Thread safety test passed")


def test_config_manager():
    """Test ConfigManager functionality."""
    print("\nTesting ConfigManager functionality...")
    
    config = config_manager
    
    # Test settings access
    settings = config.settings
    assert settings is not None, "Settings not accessible"
    print("✓ Settings accessible")
    
    # Test database URL
    db_url = config.get_database_url()
    assert db_url is not None and len(db_url) > 0, "Database URL not available"
    print("✓ Database URL accessible")
    
    # Test JWT settings
    jwt_settings = config.get_jwt_settings()
    assert "secret_key" in jwt_settings, "JWT settings incomplete"
    print("✓ JWT settings accessible")
    
    # Test boolean methods
    debug_mode = config.is_debug_mode()
    auth_disabled = config.is_auth_disabled()
    assert isinstance(debug_mode, bool), "Debug mode not boolean"
    assert isinstance(auth_disabled, bool), "Auth disabled not boolean"
    print("✓ Boolean methods working")


def test_database_manager():
    """Test DatabaseManager functionality."""
    print("\nTesting DatabaseManager functionality...")
    
    db = db_manager
    
    # Test engine access
    engine = db.engine
    assert engine is not None, "Database engine not accessible"
    print("✓ Database engine accessible")
    
    # Test session factory
    session_factory = db.session_factory
    assert session_factory is not None, "Session factory not accessible"
    print("✓ Session factory accessible")
    
    # Test session creation
    session = db.get_session()
    assert session is not None, "Database session not created"
    session.close()
    print("✓ Database session creation working")
    
    # Test connection check (this might fail if database is not configured)
    try:
        is_healthy = db.check_connection()
        print(f"✓ Connection check completed (healthy: {is_healthy})")
    except Exception as e:
        print(f"⚠ Connection check failed (expected if DB not configured): {e}")
    
    # Test connection info
    info = db.get_connection_info()
    assert isinstance(info, dict), "Connection info not a dictionary"
    assert "status" in info, "Connection info missing status"
    print("✓ Connection info accessible")


def test_service_manager():
    """Test ServiceManager functionality."""
    print("\nTesting ServiceManager functionality...")
    
    service = service_manager
    
    # Test service registration
    assert service.has_service("config"), "Config service not registered"
    assert service.has_service("database"), "Database service not registered"
    print("✓ Core services registered")
    
    # Test service access
    config_service = service.get_config_manager()
    db_service = service.get_database_manager()
    assert config_service is not None, "Config service not accessible"
    assert db_service is not None, "Database service not accessible"
    print("✓ Service access working")
    
    # Test service listing
    services = service.list_services()
    assert len(services) >= 2, "Not enough services registered"
    assert "config" in services, "Config service not in list"
    assert "database" in services, "Database service not in list"
    print("✓ Service listing working")
    
    # Test custom service registration
    test_service = {"test": "data"}
    service.register_service("test_service", test_service)
    assert service.has_service("test_service"), "Custom service not registered"
    retrieved = service.get_service("test_service")
    assert retrieved == test_service, "Custom service not retrieved correctly"
    service.unregister_service("test_service")
    assert not service.has_service("test_service"), "Custom service not unregistered"
    print("✓ Custom service registration working")
    
    # Test application status
    status = service.get_application_status()
    assert isinstance(status, dict), "Application status not a dictionary"
    assert "services_registered" in status, "Application status missing service count"
    print("✓ Application status accessible")


def test_backward_compatibility():
    """Test backward compatibility imports."""
    print("\nTesting backward compatibility...")
    
    try:
        from app.core.config import settings
        assert settings is not None, "Settings import failed"
        print("✓ Config backward compatibility working")
    except ImportError as e:
        print(f"✗ Config backward compatibility failed: {e}")
    
    try:
        from app.db.database import get_db, Base, engine
        assert get_db is not None, "get_db import failed"
        assert Base is not None, "Base import failed"
        assert engine is not None, "engine import failed"
        print("✓ Database backward compatibility working")
    except ImportError as e:
        print(f"✗ Database backward compatibility failed: {e}")


def main():
    """Run all tests."""
    print("🔍 Testing Singleton Pattern Implementation")
    print("=" * 50)
    
    try:
        test_singleton_uniqueness()
        test_thread_safety()
        test_config_manager()
        test_database_manager()
        test_service_manager()
        test_backward_compatibility()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! Singleton pattern implementation is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)