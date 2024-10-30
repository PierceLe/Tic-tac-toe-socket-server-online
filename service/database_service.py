"""
User Database Service Module

This module provides the UserDatabaseService class for managing a user database.
It allows user registration, authentication, and validation, storing users in a JSON file.

Classes:
    UserDatabaseService: A service class for managing user data.
"""

import os
import json
import bcrypt


class UserDatabaseService:
    """
    A service for managing the user database, including user registration,
    authentication, and validation of the database format.

    Attributes:
        filename (str): Path to the JSON file storing user data.
    """

    def __init__(self, filename: str):
        """
        Initializes the UserDatabaseService with a specified filename and validates
        the user database.

        Args:
            filename (str): Path to the JSON file storing user data.
        """
        self.filename = filename
        self._validate_database()

    def _validate_database(self):
        """
        Validates the structure of the user database to ensure it is a JSON array of
        user dictionaries with the required keys ("username" and "password").

        Raises:
            ValueError: If the file does not exist, is not a valid JSON format, or
                        does not conform to the expected structure.
        """
        if not os.path.exists(self.filename):
            raise ValueError(f"Error: {self.filename} path doesn't exist.")
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                users = json.load(file)
            if not isinstance(users, list):
                raise ValueError(f"Error: {self.filename} is not a JSON array.")
            for user in users:
                if not isinstance(user, dict) or \
                        set(user.keys()) != {"username", "password"}:
                    raise ValueError(f"Error: {self.filename} contains invalid user record")
        except json.JSONDecodeError as exc:
            raise ValueError(f"Error: {self.filename} is not in a valid JSON format.") from exc

    def _load_users(self):
        """
        Loads and returns the list of users from the JSON file.

        Returns:
            list: A list of user dictionaries from the database file.
        """
        with open(self.filename, 'r', encoding='utf-8') as file:
            return json.load(file)

    def save_users(self, users):
        """
        Saves the provided list of users to the JSON file.

        Args:
            users (list): The list of user dictionaries to save to the database file.
        """
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(users, file, indent=4)

    def register_user(self, username: str, password: str) -> bool:
        """
        Registers a new user by adding their username and hashed password to the database.

        Args:
            username (str): The username of the new user.
            password (str): The plaintext password of the new user.

        Returns:
            bool: True if the user was successfully registered, False if the username
                  already exists.
        """
        users = self._load_users()
        if any(user['username'] == username for user in users):
            return False
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users.append({'username': username, 'password': hashed_pw.decode('utf-8')})
        self.save_users(users)
        return True

    def user_exists(self, username: str) -> bool:
        """
        Checks if a username already exists in the database.

        Args:
            username (str): The username to check for existence.

        Returns:
            bool: True if the username exists, False otherwise.
        """
        users = self._load_users()
        return any(user['username'] == username for user in users)

    def authenticate_user(self, username: str, password: str) -> bool:
        """
        Authenticates a user by verifying the username and password against the stored data.

        Args:
            username (str): The username of the user to authenticate.
            password (str): The plaintext password of the user to authenticate.

        Returns:
            bool: True if the user credentials are correct, False otherwise.
        """
        users = self._load_users()
        user = next((user for user in users if user['username'] == username), None)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return True
        return False
