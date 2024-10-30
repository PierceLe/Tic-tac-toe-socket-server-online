"""
JoinAction Module

This module defines the JoinAction class, which allows a client to join a game room
as either a player or a viewer. It constructs and handles protocol messages for joining
a room, handles the server's response, and outputs the appropriate message to the client.
"""

import sys
from actions.action_game import Action
from actions.game.play_action import PlayAction


class JoinAction(Action):
    """
    Represents the action of joining a game room. This action enables a client to join
    a room as either a player or a viewer and handles the server response accordingly.

    Methods:
        construct_protocol_message: Constructs the protocol message for joining a room.
        to_client_stdout: Outputs a success or error message to the client's standard output.
        process_response: Processes the server's response when a client attempts to join a room.
    """

    def __init__(self):
        """
        Initializes a JoinAction with no room or mode set initially.
        """
        super().__init__()
        self.room_name = None
        self.mode = None

    def construct_protocol_message(self) -> str:
        """
        Prompts the user to enter the room name and mode, then constructs the JOIN request.

        Returns:
            str: The protocol message for joining a room in the specified mode.
        """
        room_name: str = input("Please enter the room name you want to join: ")
        mode: str = input("Please enter the mode you want to join: ")
        self.room_name = room_name
        self.mode = mode
        return f"JOIN:{room_name}:{mode}"

    def to_client_stdout(self, response: str, client) -> None:
        """
        Handles the server's response to a join request, displaying success or error messages.

        Args:
            response (str): The server's response to the join request.
            client (object): The client instance to update based on join success.
        """
        try:
            if response == "JOIN:ACKSTATUS:0":
                client.in_room = True
                if self.mode == "PLAYER":
                    client.is_player = True
                print(f"Successfully joined room {self.room_name} as a {self.mode}")
            elif response == "JOIN:ACKSTATUS:1":
                print("Error: No room named {self.room_name}", file=sys.stderr)
            elif response == "JOIN:ACKSTATUS:2":
                print("Error: The room {self.room_name} already has 2 players", file=sys.stderr)
            elif response == "JOIN:ACKSTATUS:3":
                print("Error: Invalid message format of JOIN", file=sys.stderr)
        except ValueError as e:
            print(f"An error occurred: {e}", file=sys.stderr)

    def process_response(self, conn, parts, server):
        """
        Processes the server-side response for a JOIN request, checking authentication,
        room existence, and mode validity, then sends the appropriate response to the client.

        Args:
            conn: The client connection requesting to join.
            parts (list): The parsed parts of the JOIN protocol message.
            server: The server instance containing room and user data.
        """
        if conn not in server.authenticated_users:
            conn.sendall("BADAUTH\n".encode('ascii'))
            return

        if len(parts) != 3:
            conn.sendall("JOIN:ACKSTATUS:3\n".encode('ascii'))  # Invalid message format
            return

        _, room_name, mode = parts

        if mode not in ["PLAYER", "VIEWER"]:
            conn.sendall("JOIN:ACKSTATUS:3\n".encode('ascii'))  # Invalid mode
            return

        if mode == "PLAYER":
            if room_name not in server.rooms:
                conn.sendall("JOIN:ACKSTATUS:1\n".encode('ascii'))  # Room doesn't exist
                return
            if server.rooms[room_name].is_full():
                conn.sendall("JOIN:ACKSTATUS:2\n".encode('ascii'))  # Room full
                return

            # Assign player to the room and notify participants
            server.rooms[room_name].assign_y_player(conn)
            server.rooms_dict[server.authenticated_users[conn]] = room_name
            conn.sendall("JOIN:ACKSTATUS:0\n".encode('ascii'))  # Success

            x_player_conn = server.rooms[room_name].x_player
            y_player_conn = server.rooms[room_name].y_player
            x_player = server.authenticated_users[x_player_conn]
            y_player = server.authenticated_users[y_player_conn]

            # Notify all participants of the game start
            server.rooms[room_name].started = True
            begin_message = f"BEGIN:{x_player}:{y_player}\n".encode('ascii')
            x_player_conn.sendall(begin_message)
            y_player_conn.sendall(begin_message)
            for viewer in server.rooms[room_name].viewer:
                viewer.sendall(begin_message)

            # Start the game
            room = server.rooms[room_name]
            play_action = PlayAction()
            play_action.handle_play_game(room, room.x_player, server, None)

        elif mode == "VIEWER":
            # If room exists, add the client as a viewer
            if room_name in server.rooms:
                server.rooms[room_name].add_viewer(conn)
                conn.sendall("JOIN:ACKSTATUS:0\n".encode('ascii'))  # Success
                current_player = server.authenticated_users[server.rooms[room_name].current_turn]

                if server.rooms[room_name].opposing_turn is not None:
                    connection = server.rooms[room_name].opposing_turn
                    opposing_player = server.authenticated_users[connection]
                    conn.sendall(f"INPROGRESS:{current_player}:{opposing_player}\n".encode('ascii'))

                if server.rooms[room_name].board_status != "000000000":
                    board_status = server.rooms[room_name].board_status
                    conn.sendall(f"BOARDSTATUS:{board_status}\n".encode('ascii'))
            else:
                conn.sendall("JOIN:ACKSTATUS:1\n".encode('ascii'))  # Room doesn't exist
