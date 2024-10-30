"""
TicTacToe Server Module

This module defines the TicTacToeServer class, which manages client connections, handles
messages from clients, and processes game actions. The server uses threading to handle multiple
client connections simultaneously, allowing multiple games to run concurrently.

Classes:
    TicTacToeServer: The main server class for handling Tic-Tac-Toe game logic
    and client connections.

Functions:
    main(config_file: str) -> None: Entry point for running the TicTacToe server.
"""

import socket
import sys
import threading
from typing import Dict

from models.room import Room
from creator.action_factory import action_factory
from config.application_config import ApplicationConfiguration
from service.database_service import UserDatabaseService
from actions.game.quit_action import QuitAction


class TicTacToeServer:
    """
    The TicTacToeServer class manages client connections, processes messages from clients,
    and handles the game logic for Tic-Tac-Toe.

    Attributes:
        connectors (list): A list of active client connections.
        server (socket): The main server socket for accepting new connections.
        user_db (UserDatabaseService): Service for managing user authentication.
        rooms (Dict[str, Room]): A dictionary of active game rooms.
        authenticated_users (dict): A dictionary mapping connections to authenticated usernames.
        rooms_dict (Dict[str, str]): A dictionary mapping usernames to room names.
    """
    connectors = []

    def __init__(self, config_file_path: str):
        """
        Initializes the TicTacToeServer by loading the configuration, setting up the server,
        and initializing the user database.

        Args:
            config_file_path (str): Path to the server configuration file.
        """
        try:
            config = ApplicationConfiguration(config_file_path)
            port = config.get('port')
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)
        except (KeyError, ValueError) as e:
            print(f"Configuration error: {e}")
            sys.exit(1)

        # Set up the server socket
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(('localhost', port))
            self.server.listen()
        except socket.error as e:
            print(f"Socket error: {e}")
            sys.exit(1)

        # Initialize the user database service and game rooms
        self.user_db = UserDatabaseService(config.get('userDatabase'))
        self.rooms: Dict[str, Room] = {}
        self.authenticated_users: dict = {}
        self.rooms_dict: Dict[str, str] = {}

    def handle_client(self, conn):
        """
        Handles incoming messages from a client connection.

        Args:
            conn (socket): The client connection socket.
        """
        connected = True
        while connected:
            try:
                message = conn.recv(8192).decode('ascii')
                if message:
                    print(f"\033[92m{message}\033[0m")
                    self.process_message(conn, message)
                else:
                    self.process_disconnect(conn)
                    connected = False
            except ConnectionResetError:
                print("Client disconnected unexpectedly.")
                self.process_disconnect(conn)
                connected = False
        conn.close()

    def process_disconnect(self, conn):
        """
        Processes client disconnection by cleaning up resources and removing the client
        from authenticated users.

        Args:
            conn (socket): The client connection socket.
        """
        if QuitAction.check_join_room(conn, self):
            action = QuitAction()
            action.process_response(conn, None, self)
        self.authenticated_users.pop(conn, None)

    def process_message(self, conn, message):
        """
        Processes a message received from a client by creating the appropriate action
        and invoking its response handling.

        Args:
            conn (socket): The client connection socket.
            message (str): The message received from the client.
        """
        parts = message.strip().split(':')
        command = parts[0]
        action = action_factory(command)
        action.process_response(conn, parts, self)

    def start(self):
        """
        Starts the server, continuously accepting new connections and spawning threads
        to handle each client connection.
        """
        print("Server started and listening for connections...")
        while True:
            conn, _ = self.server.accept()
            self.connectors.append(conn)
            client_thread = threading.Thread(target=self.handle_client, args=(conn,))
            client_thread.start()


def main(config_file: str):
    """
    Entry point for starting the TicTacToe server.

    Args:
        config_file (str): Path to the server configuration file.
    """
    try:
        server = TicTacToeServer(config_file)
        server.start()
    except FileNotFoundError:
        print("Error: Configuration file not found.")
        sys.exit(1)

    except (KeyError, ValueError) as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    except socket.error as e:
        print(f"Socket error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise ValueError("Error: Expecting 1 argument: <server config path>")
    main(sys.argv[1])
