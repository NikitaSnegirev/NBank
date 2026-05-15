import os
from typing import Any
from pathlib import Path


class Config:
    _instance = None
    _properties = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            config_path = Path('resources/config.properties')
            if not config_path.exists():
                raise ImportError(f'{config_path}: config.properties not found')
            with open(config_path, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        cls._properties[key] = value
        return cls._instance

    @staticmethod
    def get(key: str, default_value: Any = None) -> Any:
        # Allow overriding config.properties via environment variables (useful for CI / Docker / different backends).
        env_val = os.getenv(key) or os.getenv(key.upper())
        if env_val is not None:
            return env_val
        return Config()._properties.get(key, default_value)