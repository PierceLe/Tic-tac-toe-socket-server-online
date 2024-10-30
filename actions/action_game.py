"""
Action Module

This module defines the `Action` abstract base class, which represents a generic action
that can be initiated by a client in a client-server architecture. Each specific action
(e.g., LOGIN, REGISTER) will inherit from this class and implement its methods to
define protocol messages, handle server responses, and process client responses.

Classes:
    Action (ABC): An abstract base class that provides a template for different types
                  of client actions, with abstract methods for constructing protocol
                  messages, handling server responses, and processing responses from the server.
"""

from abc import ABC, abstractmethod


class Action(ABC):
    """
    An abstract base class representing a generic action that can be taken by
    a client. Each specific action will inherit from this
    class and implement its methods to define how the action constructs protocol
    messages, handles server responses, and processes responses from the server.
    """

    @abstractmethod
    def construct_protocol_message(self) -> str:
        """
        Constructs a protocol message string specific to the action.

        Returns:
            str: The protocol message in the required format for the action.

        This method should be implemented by subclasses to define the structure
        of the protocol message for a particular action (e.g., LOGIN, REGISTER).
        """

    @abstractmethod
    def to_client_stdout(self, response: str, client) -> None:
        """
        Processes a server response for this action and outputs relevant information
        to the client’s stdout or stderr.

        Args:
            response (str): The server's response message for this action.
            client: The client instance, allowing this method to modify client state if needed.

        This method should be implemented by subclasses to define how responses
        from the server are interpreted and displayed to the client for a particular action.
        """

    @abstractmethod
    def process_response(self, conn, parts, server):
        """
        Processes an incoming message from a client and determines the appropriate
        server response for this action.

        Args:
            conn: The client connection instance.
            parts (str): The incoming message string from the client.
            server: The server instance, which contains necessary resources like user
                    database or authenticated users.

        This method should be implemented by subclasses to handle server-side processing
        of a specific client action. It usually involves validation and constructing
        a response message to be sent back to the client.
        """

    @staticmethod
    def filter_protocol_message(message) -> list:
        """
        Splits and filters the protocol message into parts based on the colon delimiter.

        Args:
            message (str): The protocol message string to be split.

        Returns:
            list: A list of strings, split by the colon character, which represents
                  the components of the protocol message.

        This static method provides a utility to standardize the splitting of protocol
        messages into components (e.g., action type, parameters) for easier processing.
        """
        return message.strip().split(':')
