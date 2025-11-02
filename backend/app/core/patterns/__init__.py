"""
Design Patterns Module

This module contains various design pattern implementations used throughout the application.
Currently includes:
- Singleton Pattern: For managing single instances of classes like database and config managers
"""

from .singleton import Singleton, SingletonMeta, SingletonABCMeta

__all__ = ["Singleton", "SingletonMeta", "SingletonABCMeta"]