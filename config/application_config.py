"""
Application Configuration Module

This module provides the ApplicationConfiguration class to load, validate, and access
configuration settings for the TicTacToe server. The configuration is expected in JSON format.

Classes:
    ApplicationConfiguration: Loads, validates, and provides access to configuration settings.
"""

import json
import os


class ApplicationConfiguration:
    """
    Manages application configuration by loading, validating, and providing access
    to configuration settings.

    Attributes:
        _config (dict): Stores the configuration settings after validation.
    """

    def __init__(self, config_path: str):
        """
        Initializes the ApplicationConfiguration by loading and validating the config file.

        Args:
            config_path (str): Path to the JSON configuration file.
        """
        self._config = self._load_config(config_path)

    @staticmethod
    def _load_config(path: str) -> dict:
        """
        Private method to load and validate the configuration file.

        Args:
            path (str): Path to the JSON configuration file.

        Returns:
            dict: The loaded configuration settings.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file is not in valid JSON format.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Error: {path} doesn't exist.")

        with open(path, 'r', encoding='utf-8') as file:
            try:
                config = json.load(file)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Error: {path} is not in a valid JSON format.") from exc

        ApplicationConfiguration._validate_config(config, path)
        return config

    @staticmethod
    def _validate_config(config: dict, path: str) -> None:
        """
        Private method to validate necessary configuration keys and types.

        Args:
            config (dict): Configuration data to validate.
            path (str): Path to the JSON configuration file.

        Raises:
            KeyError: If required keys are missing.
            ValueError: If the port number is out of range.
        """
        required_keys = ['port', 'userDatabase']
        missing_keys = [key for key in required_keys if key not in config]

        if missing_keys:
            missing_key_list = ', '.join(sorted(missing_keys))
            raise KeyError(f"Error: {path} missing key(s): {missing_key_list}")

        if not (isinstance(config['port'], int) and (1024 <= config['port'] <= 65535)):
            raise ValueError("Error: port number out of range")

        if not os.path.isabs(config['userDatabase']):
            config['userDatabase'] = os.path.join(os.getcwd(), config['userDatabase'])

    def get(self, key: str):
        """
        Public method to access configuration values safely.

        Args:
            key (str): The configuration key to retrieve.

        Returns:
            The value associated with the specified key.
        """
        return self._config.get(key)

    def __str__(self) -> str:
        """
        Provide a string representation of the configuration for debugging.

        Returns:
            str: A JSON-formatted string of the configuration.
        """
        return json.dumps(self._config, indent=4)
