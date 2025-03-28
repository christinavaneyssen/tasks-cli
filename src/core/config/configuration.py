import configparser
import os

from src import BASE_DIR


class Configuration:
    _instance = None
    _config: configparser.ConfigParser | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self) -> None:
        """Load configuration from config.ini file."""
        self._config = configparser.ConfigParser()
        config_path = os.path.join(BASE_DIR, 'config.ini')
        if os.path.exists(config_path):
            self._config.read(config_path)

    def get(self, section: str, key: str) -> str | int | bool | None:
        """Get a configuration value."""
        if self._config is None:
            self._load_config()
        try:
            return self._config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return None

    def get_section(self, section: str) -> dict[str, str]:
        """Get an entire configuration section as dictionary."""
        if self._config is None:
            self._load_config()

        if section in self._config:
            return dict(self._config[section])
        return {}
