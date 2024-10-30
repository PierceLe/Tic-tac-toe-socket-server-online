"""
QuitAction Module

This module defines the QuitAction class, which handles the process of a player forfeiting
the game and notifying all relevant parties in the room.
"""

from actions.action_game import Action


class QuitAction(Action):
    """
    Handles the action of a player forfeiting the game. This action notifies the opponent,
    viewers, and updates the server state to reflect the forfeit.
    """

    def construct_protocol_message(self) -> str:
        """
        Constructs the protocol message for a forfeit action.

        Returns:
            str: A string indicating a forfeit action, formatted as "FORFEIT".
        """
        return "FORFEIT"

    def to_client_stdout(self, response: str, client) -> None:
        """
        Updates the client's state to reflect that they are no longer in a room or
        participating as a player.

        Args:
            response (str): The server's response message (not used in this case).
            client: The client instance to update.
        """
        client.in_room = False
        client.is_player = False

    @staticmethod
    def check_join_room(conn, server) -> bool:
        """
        Checks if the client associated with `conn` has joined a room.

        Args:
            conn: The client's connection object.
            server: The server instance containing room and user data.

        Returns:
            bool: True if the user is in a room, False otherwise.
        """
        return server.authenticated_users.get(conn) in server.rooms_dict

    def process_response(self, conn, parts, server):
        """
        Processes the server-side response for a forfeit action. Notifies the opponent
        and any viewers in the room that the game has ended due to forfeit.

        Args:
            conn: The client connection for the player forfeiting.
            parts (unused): Not used in this implementation but maintained for consistency.
            server: The server instance containing room and user data.
        """
        if conn not in server.authenticated_users:
            conn.sendall("BADAUTH\n".encode('ascii'))
            return

        if not QuitAction.check_join_room(conn, server):
            try:
                conn.sendall("NOROOM\n".encode('ascii'))
            except (ConnectionError, OSError):
                pass
            return

        room_name = server.rooms_dict.get(server.authenticated_users[conn])
        if not room_name or room_name not in server.rooms:
            return

        room = server.rooms[room_name]
        x_player_conn = room.x_player
        y_player_conn = room.y_player

        if y_player_conn is None:
            return

        # Determine the winner and notify both players and viewers of the game end
        winner = (server.authenticated_users[x_player_conn]
                  if conn == y_player_conn else server.authenticated_users[y_player_conn])
        game_end_message = f"GAMEEND:{room.board_status}:2:{winner}\n".encode('ascii')

        for player_conn in [x_player_conn, y_player_conn]:
            if player_conn is not None:
                try:
                    player_conn.sendall(game_end_message)
                except (ConnectionError, OSError):
                    pass

        for viewer in room.viewer:
            try:
                viewer.sendall(game_end_message)
            except (ConnectionError, OSError):
                pass

        owner = server.authenticated_users.get(x_player_conn)
        if owner:
            del server.rooms_dict[owner]
            del server.rooms[room_name]
