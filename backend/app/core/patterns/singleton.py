from abc import ABC, ABCMeta
from typing import Optional, Any
import threading


class SingletonMeta(type):
    """
    Thread-safe Singleton metaclass.
    This metaclass ensures that only one instance of a class exists
    and provides thread-safe initialization.
    """
    
    _instances = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class SingletonABCMeta(SingletonMeta, ABCMeta):
    """
    Metaclass that combines Singleton and ABC metaclasses to avoid conflicts.
    """
    pass


class Singleton(ABC, metaclass=SingletonABCMeta):
    """
    Abstract base class for implementing Singleton pattern.
    
    Any class that inherits from this will automatically become a singleton
    with thread-safe initialization.
    """
    
    def __init__(self):
        """Initialize the singleton instance."""
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self._setup()
    
    def _setup(self):
        """
        Override this method to perform actual initialization.
        This method will only be called once during the lifetime of the singleton.
        """
        pass
    
    @classmethod
    def get_instance(cls):
        """
        Get the singleton instance.
        
        Returns:
            The singleton instance of the class.
        """
        return cls()
    
    def reset(self):
        """
        Reset the singleton instance.
        This method should be used carefully, mainly for testing purposes.
        """
        if hasattr(self, '_initialized'):
            delattr(self, '_initialized')
        self._setup()