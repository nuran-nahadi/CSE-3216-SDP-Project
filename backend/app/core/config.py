# This file is kept for backward compatibility
# New configuration management is handled by ConfigManager singleton
# Import the new config manager for access to settings

from app.core.config_manager import config_manager, settings

# For backward compatibility, expose the settings object directly
__all__ = ["settings", "config_manager"]