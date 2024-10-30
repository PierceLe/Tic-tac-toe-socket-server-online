"""
RegisterAction Module

This module defines the RegisterAction class, which handles user registration by prompting
for a username and password, constructing a protocol message, and processing server responses.
"""

import sys
from actions.action_game import Action


class RegisterAction(Action):
    """
    Handles the REGISTER action for a client, including constructing the registration
    protocol message, processing server responses, and sending the user's credentials
    to the server to create a new account.
    """

    def __init__(self):
        """
        Initializes a RegisterAction instance with username and password attributes.
        """
        super().__init__()
        self.username = None
        self.password = None

    def construct_protocol_message(self) -> str:
        """
        Prompts the user to enter their desired username and password, constructs
        the REGISTER protocol message, and returns it.

        Returns:
            str: A formatted registration message in the form of "REGISTER:<username>:<password>"
        """
        username_verified = False
        username = ""
        while True:
            if not username_verified:
                username = input("Enter username: ")
                if len(username) > 20:
                    print("Error: username length limitation is 20 characters")
                    continue
                username_verified = True
            password = input("Enter password: ")
            if len(password) > 20:
                print("Error: password length limitation is 20 characters")
                continue
            self.username = username
            self.password = password
            return f"REGISTER:{username}:{password}"

    def to_client_stdout(self, response: str, client) -> None:
        """
        Processes the server's response to a REGISTER request and prints
        appropriate messages based on the ACKSTATUS code.

        Args:
            response (str): The server's response message.
            client: The client instance (not directly used in this method).

        ACKSTATUS Codes:
            - "0": Successful account creation.
            - "1": Username already exists.
            - "2": Invalid REGISTER message format.
        """
        try:
            if response == "REGISTER:ACKSTATUS:0":
                print(f"Successfully created user account {self.username}")
            elif response == "REGISTER:ACKSTATUS:1":
                print("Error: User already exists", file=sys.stderr)
            elif response == "REGISTER:ACKSTATUS:2":
                print("Error: Invalid message format of REGISTER", file=sys.stderr)
        except ValueError as e:
            print(f"An error occurred: {e}", file=sys.stderr)

    def process_response(self, conn, parts, server):
        """
        Processes a REGISTER request message from the client, verifies the validity
        of the username and password, and sends an appropriate ACKSTATUS response
        back to the client.

        Args:
            conn: The connection instance representing the client connection.
            parts (list): A list of parts extracted from the protocol message.
            server: The server instance to access the user database for registration.

        Protocol Logic:
            - Sends "REGISTER:ACKSTATUS:2" if the message format is invalid.
            - Sends "REGISTER:ACKSTATUS:3" if the username or password exceeds 20 characters.
            - Sends "REGISTER:ACKSTATUS:1" if the username already exists.
            - Sends "REGISTER:ACKSTATUS:0" if the registration is successful.
        """
        if len(parts) != 3:
            conn.sendall("REGISTER:ACKSTATUS:2\n".encode('ascii'))
            return
        _, username, password = parts
        if len(username) > 20 or len(password) > 20:
            conn.sendall("REGISTER:ACKSTATUS:3\n".encode('ascii'))
        elif server.user_db.register_user(username, password):
            conn.sendall("REGISTER:ACKSTATUS:0\n".encode('ascii'))
        else:
            conn.sendall("REGISTER:ACKSTATUS:1\n".encode('ascii'))
