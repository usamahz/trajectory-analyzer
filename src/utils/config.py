# Copyright 2024
# Author: Usamah Zaheer
import yaml
from pathlib import Path

class Config:
    """
    Singleton class for managing configuration settings from YAML file.
    
    Attributes:
        _instance (Config): Singleton instance
        _config (dict): Loaded configuration data
    """

    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """
        Load configuration from default.yaml file.
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid
        """
        config_path = Path(__file__).parent.parent.parent / 'config' / 'default.yaml'
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
    
    @property
    def config(self):
        return self._config
    
    def get(self, *keys, default=None):
        """
        Safely retrieve nested configuration values.
        
        Args:
            *keys: Variable number of keys for nested access
            default: Default value if key path doesn't exist
            
        Returns:
            Any: Configuration value or default if not found
        """
        value = self._config
        for key in keys:
            try:
                value = value[key]
            except (KeyError, TypeError):
                return default
        return value 