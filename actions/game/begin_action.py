"""
BeginAction Module

This module defines the BeginAction class, which represents the action of beginning
a game match between two players. It constructs and handles protocol messages that
indicate the start of a match and outputs the start message to the client.
"""

from actions.action_game import Action


class BeginAction(Action):
    """
    Represents the action for beginning a game match between two players.

    This action constructs and handles protocol messages indicating the start of a match,
    as well as outputs the start message to the client.

    Methods:
        construct_protocol_message: Constructs the protocol message for the action.
        to_client_stdout: Outputs a formatted message to the client's standard output.
        process_response: Processes the server's response, though it does not alter connection
                          or server states for this action.
    """

    def construct_protocol_message(self) -> str:
        """
        Constructs the protocol message for beginning the game.

        Returns:
            str: An empty string as no specific protocol message is required to start the game.
        """
        return ""

    def to_client_stdout(self, response: str, client) -> None:
        """
        Outputs a message to the client indicating the start of the game match.

        Args:
            response (str): The protocol response message containing player information.
            client (object): The client instance, though unused in this method.
        """
        parts = Action.filter_protocol_message(response)
        print(
            f"Match between {parts[1]} and {parts[2]} will commence, "
            f"it is currently {parts[1]}'s turn."
        )

    def process_response(self, conn, parts, server):
        """
        Processes the response from the server. This action does not modify
        connection or server state.

        Args:
            conn (socket): The connection object to the server.
            parts (list): The parsed parts of the protocol message.
            server (object): The server instance handling the game.
        """
