"""
InprogressAction Module

This module defines the InprogressAction class, which notifies a viewer client of an
ongoing match, including details about the current turn player and the opposing player.
"""

from actions.action_game import Action


class InprogressAction(Action):
    """
    Represents the action for notifying a viewer client of an ongoing match.

    This action is triggered when a viewer joins a game that is already in progress. It
    displays the current status of the game, including which player's turn it is.

    Methods:
        construct_protocol_message: Constructs the protocol message for this action.
        to_client_stdout: Outputs a formatted message indicating the current state of the
                          match and whose turn it is.
        process_response: Processes the server's response; does not alter connection
                          or server states for this action.
    """

    def construct_protocol_message(self) -> str:
        """
        Constructs the protocol message for in-progress game notification.

        Returns:
            str: An empty string as no specific protocol message is needed to notify the client.
        """
        return ""

    def to_client_stdout(self, response: str, client) -> None:
        """
        Outputs the current match status to the client's standard output.

        Args:
            response (str): The protocol response message containing the current turn player
                            and opposing player information.
            client (object): The client instance, though unused in this method.
        """
        parts = Action.filter_protocol_message(response)
        print(
            f"Match between {parts[1]} and {parts[2]} is currently in progress, "
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
