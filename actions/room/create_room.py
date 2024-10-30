"""
CreateRoomAction Module

This module defines the CreateRoomAction class, which allows a client to create a new game room.
It constructs and handles protocol messages for creating a room, processes server responses,
and displays appropriate messages to the client.
"""

import sys
import re
from models.room import Room
from actions.action_game import Action


class CreateRoomAction(Action):
    """
    Handles the CREATE action for a client, including constructing the room creation
    protocol message, processing server responses, and creating a new game room on the server.
    """

    def __init__(self):
        """
        Initializes a CreateRoomAction instance with the room name attribute.
        """
        super().__init__()
        self.name = None

    def construct_protocol_message(self) -> str:
        """
        Prompts the user to enter the room name and constructs the CREATE request.

        Returns:
            str: The protocol message for creating a new room with the specified name.
        """
        name: str = input("Enter the room name you want to create: ")
        self.name = name
        return f"CREATE:{name}"

    def to_client_stdout(self, response: str, client) -> None:
        """
        Processes the server's response to a CREATE request and prints appropriate
        messages based on the ACKSTATUS code.

        Args:
            response (str): The server's response message.
            client: The client instance to update based on room creation success.

        ACKSTATUS Codes:
            - "0": Room created successfully.
            - "1": Invalid room name.
            - "2": Room already exists.
            - "3": Maximum number of rooms reached.
            - "4": Invalid CREATE message format.
        """
        try:
            parts: list = Action.filter_protocol_message(response)
            if response == "BADAUTH":
                print("Error: You must be logged in to perform this action.", file=sys.stderr)
                return

            if len(parts) < 3 or parts[1] != "ACKSTATUS":
                print("Error: Unexpected response format.", file=sys.stderr)
                return

            ack_status = parts[2]
            if ack_status == "0":
                client.in_room = True
                client.owner = True
                client.in_turn = True
                print(f"Successfully created room {self.name}. Waiting for other players to join.")
            elif ack_status == "1":
                print("Error: Room name is invalid.", file=sys.stderr)
            elif ack_status == "2":
                print("Error: Room already exists.", file=sys.stderr)
            elif ack_status == "3":
                print("Error: Maximum number of rooms reached (256).", file=sys.stderr)
            elif ack_status == "4":
                print("Error: Invalid room creation format.", file=sys.stderr)
            else:
                print(f"Error: Unrecognized ACKSTATUS {ack_status}.", file=sys.stderr)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)

    def process_response(self, conn, parts, server):
        """
        Processes the server-side response for a CREATE request, checking authentication,
        room name validity, and maximum room limit, then sends an appropriate response.

        Args:
            conn: The client connection requesting to create a room.
            parts (list): The parsed parts of the CREATE protocol message.
            server: The server instance containing room and user data.
        """
        if conn not in server.authenticated_users:
            conn.sendall("BADAUTH\n".encode('ascii'))
            return

        if len(parts) != 2:
            conn.sendall("CREATE:ACKSTATUS:4\n".encode('ascii'))  # Invalid message format
            return

        room_name = parts[1]

        if not re.match(r'^[a-zA-Z0-9-_ ]+$', room_name) or len(room_name) > 20:
            conn.sendall("CREATE:ACKSTATUS:1\n".encode('ascii'))  # Invalid room name
            return

        if room_name in server.rooms:
            conn.sendall("CREATE:ACKSTATUS:2\n".encode('ascii'))  # Room already exists
            return

        if len(server.rooms) >= 256:
            conn.sendall("CREATE:ACKSTATUS:3\n".encode('ascii'))  # Max room limit reached
            return

        # Create the room and assign the client as the 'x' player
        server.rooms[room_name] = Room(room_name)
        server.rooms[room_name].assign_x_player(conn)
        server.rooms_dict[server.authenticated_users[conn]] = room_name
        conn.sendall("CREATE:ACKSTATUS:0\n".encode('ascii'))
