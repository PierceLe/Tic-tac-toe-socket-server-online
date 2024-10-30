"""
RoomListAction Module

This module defines the RoomListAction class, which is used to request
and display a list of available rooms that a user can join as
either a player or a viewer.
"""

import sys
from models.room import Room
from actions.action_game import Action


class RoomListAction(Action):
    """
    Represents an action to request a list of available rooms, either as a player or viewer.

    This class prompts the user to choose the mode (PLAYER/VIEWER) and constructs a protocol
    message for requesting the room list. It also handles the server's response and displays
    the list of rooms to the client.
    """

    def __init__(self):
        """
        Initializes a RoomListAction with no mode set initially.
        """
        super().__init__()
        self.mode = None

    def construct_protocol_message(self) -> str:
        """
        Prompts the user to choose the mode and constructs the ROOMLIST request.

        Returns:
            str: The protocol message for requesting the room list in the selected mode.
        """
        mode: str = input("Do you want to have a room list as a player or viewer? (PLAYER/VIEWER) ")
        self.mode = mode
        return f"ROOMLIST:{mode}"

    def to_client_stdout(self, response: str, client) -> None:
        """
        Handles the server's response to the room list request and displays the appropriate message
        or error to the client.

        Args:
            response (str): The response message from the server.
            client: The client instance (unused in this method).
        """
        try:
            parts: list = Action.filter_protocol_message(response)
            if response == "BADAUTH":
                print("Error: You must be logged in to perform this action", file=sys.stderr)
            elif parts[1] == "ACKSTATUS":
                ack_status = parts[2]
                if ack_status == "0":
                    print(f"Room available to join as {self.mode} are: ")
                    for room in parts[3].split(","):
                        print(room)
                elif ack_status == "1":
                    print("Error: Please input a valid mode.", file=sys.stderr)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)

    def process_response(self, conn, parts, server):
        """
        Processes the server-side response for the ROOMLIST action, checking authentication
        and mode validity, and sends the appropriate response back to the client.

        Args:
            conn: The client connection requesting the room list.
            parts (list): The parsed parts of the ROOMLIST protocol message.
            server: The server instance containing room and user data.
        """
        if conn not in server.authenticated_users:
            conn.sendall("BADAUTH\n".encode('ascii'))
            return

        if len(parts) != 2:
            conn.sendall("ROOMLIST:ACKSTATUS:1\n".encode('ascii'))
            return

        _, mode = parts
        if mode == "VIEWER":
            room_names = ",".join(Room.get_viewable_room(server.rooms))
            conn.sendall(f"ROOMLIST:ACKSTATUS:0:{room_names}\n".encode('ascii'))
        elif mode == "PLAYER":
            room_names = ",".join(sorted(Room.get_playable_room(server.rooms)))
            conn.sendall(f"ROOMLIST:ACKSTATUS:0:{room_names}\n".encode('ascii'))
        else:
            conn.sendall("ROOMLIST:ACKSTATUS:1\n".encode('ascii'))
