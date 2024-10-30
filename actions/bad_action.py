"""
BadAction Module

This module defines the BadAction class, which represents an invalid or unrecognized action.
BadAction provides a default response for any actions that do not match valid types, returning
a "BAD:ACTION" message to indicate an error.
"""

from actions.action_game import Action


class BadAction(Action):
    """
    Represents an invalid or unrecognized action. This class provides a default
    response for any actions that do not match valid types, returning a "BAD:ACTION"
    message to indicate an error.

    This class is used as a fallback when the client sends an unknown or improperly
    formatted action. It prevents the server from breaking or misinterpreting unexpected
    messages.
    """

    def construct_protocol_message(self) -> str:
        """
        Constructs the protocol message for an invalid action.

        Returns:
            str: A string indicating an invalid action, formatted as "BAD:ACTION".

        This message is a default placeholder to communicate that the action sent
        by the client is not recognized by the server.
        """
        return "BAD:ACTION"

    def to_client_stdout(self, response: str, client) -> None:
        """
        Handles server responses for a BadAction. Since BadAction is not expected to
        produce any meaningful client output, this method is essentially a placeholder.

        Args:
            response (str): The server's response message (not used in this case).
            client: The client instance (not used in this case).
        """

    def process_response(self, conn, parts, server):
        """
        Processes a server-side response for a BadAction. As this action type is invalid,
        no response is required or expected from the server. This method acts as a
        placeholder to ensure protocol compliance.

        Args:
            conn: The connection object (not used in this case).
            parts: The message object (not used in this case).
            server: The server instance (not used in this case).
        """
