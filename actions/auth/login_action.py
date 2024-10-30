"""
LoginAction Module

This module defines the LoginAction class, which handles user login by prompting
for a username and password, constructing a protocol message, and processing
server responses.
"""

import sys
from actions.action_game import Action


class LoginAction(Action):
    """
    Handles the LOGIN action for a client, including constructing the login
    protocol message, processing server responses, and sending the client's
    credentials to the server.
    """

    def __init__(self):
        """
        Initializes a LoginAction instance with username and password attributes.
        """
        super().__init__()
        self.username = None
        self.password = None

    def construct_protocol_message(self) -> str:
        """
        Prompts the user to enter their username and password, constructs
        the LOGIN protocol message, and returns it.

        Returns:
            str: A formatted login message in the form of "LOGIN:<username>:<password>"
        """
        username: str = input("Enter username: ")
        password: str = input("Enter password: ")
        self.username = username
        self.password = password
        return f"LOGIN:{username}:{password}"

    def to_client_stdout(self, response: str, client) -> None:
        """
        Processes the server's response to a LOGIN request and prints
        appropriate messages based on the ACKSTATUS code.

        Args:
            response (str): The server's response message.
            client: The client instance, used to set authentication status.

        ACKSTATUS Codes:
            - "0": Successful login
            - "1": Username not found
            - "2": Incorrect password
            - "3": Invalid LOGIN message format
            - "4": Account is already logged in from another client
        """
        try:
            parts = Action.filter_protocol_message(response)
            if parts[1] == "ACKSTATUS":
                ack_status = parts[2]
                if ack_status == "0":
                    print(f"Welcome {self.username}")
                    client.name = self.username
                    client.is_authenticated = True
                elif ack_status == "1":
                    print("Error: User not found", file=sys.stderr)
                elif ack_status == "2":
                    print("Error: Wrong password", file=sys.stderr)
                elif ack_status == "3":
                    print("Error: Invalid message format of LOGIN", file=sys.stderr)
                elif ack_status == "4":
                    print("Error: The account has been logged in by another user", file=sys.stderr)
            else:
                print(f"Error: {response}", file=sys.stderr)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)

    def process_response(self, conn, parts, server):
        """
        Processes a LOGIN request message from the client, verifies the username
        and password, and sends an appropriate ACKSTATUS response back to the client.

        Args:
            conn: The connection instance representing the client connection.
            parts (list): A list of parts extracted from the protocol message.
            server: The server instance to access the user database and authenticated users.

        Protocol Logic:
            - Sends "LOGIN:ACKSTATUS:3" if the message format is invalid.
            - Sends "LOGIN:ACKSTATUS:1" if the username is not found.
            - Sends "LOGIN:ACKSTATUS:4" if the account is already logged in from another client.
            - Sends "LOGIN:ACKSTATUS:0" if the login is successful.
            - Sends "LOGIN:ACKSTATUS:2" if the password is incorrect.
        """
        if len(parts) != 3:
            conn.sendall("LOGIN:ACKSTATUS:3\n".encode('ascii'))
            return
        _, username, password = parts
        if not server.user_db.user_exists(username):
            conn.sendall("LOGIN:ACKSTATUS:1\n".encode('ascii'))
        elif server.user_db.authenticate_user(username, password):
            if username in server.authenticated_users.values():
                conn.sendall("LOGIN:ACKSTATUS:4\n".encode('ascii'))
            else:
                server.authenticated_users[conn] = username
                conn.sendall("LOGIN:ACKSTATUS:0\n".encode('ascii'))
        else:
            conn.sendall("LOGIN:ACKSTATUS:2\n".encode('ascii'))
