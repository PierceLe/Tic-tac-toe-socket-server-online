"""
TicTacToe Client Module

This module defines the TicTacToeClient class, which connects to a server to participate
in a Tic-Tac-Toe game. It includes methods for sending and receiving messages, managing
game state, and handling client disconnection.

Classes:
    TicTacToeClient: The main client class for handling game state and server communication.

Functions:
    main(args): Entry point for running the TicTacToe client.
    receive_messages(client_socket): Listens for messages from the server and processes them.
"""

import socket
import sys
import threading
from creator.action_factory import action_factory, save_global_variable, get_global_variable


class TicTacToeClient:
    """
    The TicTacToeClient class manages the connection to the Tic-Tac-Toe server, game state,
    and message sending/receiving.

    Attributes:
        client (socket): The socket connection to the server.
        name (str): Username of the client.
        is_authenticated (bool): Whether the client is authenticated.
        in_room (bool): Whether the client is in a room.
        can_quit (bool): Whether the client can quit the game.
        is_player (bool): Whether the client is a player (vs. viewer).
        owner (bool): Whether the client is the room owner.
        in_turn (bool): Whether it is the client's turn in the game.
        disconnected (Event): Event to signal disconnection.
    """
    def __init__(self, host: str, port: int):
        """
        Initializes the client by connecting to the specified server and setting up attributes.

        Args:
            host (str): The server's hostname or IP address.
            port (int): The server's port number.

        Raises:
            Exception: If the client cannot connect to the server.
        """
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((host, port))
        except (socket.error, ConnectionRefusedError) as exc:
            raise ConnectionRefusedError(
                f"Error: cannot connect to server at {host} and {port}."
            ) from exc
        self.name = None
        self.is_authenticated = False
        self.in_room = False
        self.can_quit = False
        self.is_player = False
        self.owner = False
        self.in_turn = False
        self.disconnected = threading.Event()

    def close(self):
        """
        Closes the connection to the server and sets the disconnected event.
        """
        self.disconnected.set()
        try:
            self.client.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.client.close()

    def after_game(self):
        """
        Resets the client's game-related attributes after a game ends.
        """
        self.in_room = False
        self.can_quit = False
        self.is_player = False
        self.owner = False
        self.in_turn = False


def main(args):
    """
    Entry point for running the TicTacToe client.

    Args:
        args (list): Command-line arguments including server address and port.

    Raises:
        ValueError: If the number of arguments or port number is invalid.
    """
    if len(args) != 2:
        raise ValueError("Error: Expecting 2 arguments: <server address> <port>")

    host = args[0]
    try:
        port = int(args[1])
    except ValueError as exc:
        raise ValueError(f"Error: Invalid port number {args[1]}") from exc

    client = TicTacToeClient(host, port)
    thread_receive = threading.Thread(target=receive_messages, args=(client,))
    thread_receive.start()

    while not client.disconnected.is_set():
        try:
            if client.can_quit:
                client.close()
                break
            user_input = input().strip().upper()
        except (EOFError, BrokenPipeError):
            if not client.in_room or client.is_player:
                client.close()
                break
        except Exception:
            client.close()
            break

        if user_input.lower() == "quit":
            if not client.in_room or client.is_player:
                client.close()
                break

        action_game = action_factory(user_input)
        message = action_game.construct_protocol_message()

        if message.startswith("PLACE"):
            try:
                _, x, y = message.split(":")
                if not (0 <= int(x) <= 2 and 0 <= int(y) <= 2):
                    print("Position invalid")
                    message = "ERROR"
            except ValueError:
                message = "ERROR"

        if message != "ERROR":
            save_global_variable(action_game)
            client.client.sendall(message.encode('ascii'))

    client.close()
    thread_receive.join()


def receive_messages(client_socket):
    """
    Listens for messages from the server and processes them based on message type.

    Args:
        client_socket (TicTacToeClient): The client instance.
    """

    try:
        while True:
            response = client_socket.client.recv(8192).decode('utf-8').strip()
            print(f"\033[92m{response}\033[0m")
            if not response:
                break

            action_type = response.split(":")[0].strip()
            action_game = action_factory(action_type)
            get_global_variable(action_game)

            if response.startswith("GAMEEND"):
                if client_socket.in_room and not client_socket.is_player:
                    client_socket.can_quit = True
                    client_socket.close()
                client_socket.in_room = False
            action_game.to_client_stdout(response, client_socket)

    except Exception:
        pass


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception as e:
        print(e)
