"""
BoardStatusAction Module

This module defines the BoardStatusAction class, which handles the display of the current
game board status for a Tic-Tac-Toe match. It interprets the board state sent by the server
and formats it into a 3x3 grid to be displayed on the client side.

Classes:
    BoardStatusAction (Action): An action for updating the board display based on the
                                server-provided status.
"""

from actions.action_game import Action


class BoardStatusAction(Action):
    """
    Represents the action for handling and displaying the current game board status.

    This action interprets the board status sent by the server and prints the
    current state of the game board to the client's standard output.

    Methods:
        construct_protocol_message: Constructs the protocol message for this action.
        to_client_stdout: Outputs a formatted board to the client's standard output
                          and indicates whose turn it is.
        process_response: Processes the server's response but does not alter connection
                          or server states for this action.
    """

    def construct_protocol_message(self) -> str:
        """
        Constructs the protocol message for board status updates.

        Returns:
            str: An empty string as no specific protocol message is needed to request board status.
        """
        return ""

    def to_client_stdout(self, response: str, client) -> None:
        """
        Outputs the current board status to the client's standard output.

        Args:
            response (str): The protocol response message containing the board status as a
            9-character string.
            client (object): The client instance to track the current turn.
        """
        # Extract the board status from the response
        status = Action.filter_protocol_message(response)[1]

        # Define a mapping for each character in the status string
        symbol_map = {
            '1': 'X',  # Player X marker
            '2': 'O',  # Player O marker
            '0': ' '  # Empty space
        }

        # Map each character in the status to its corresponding symbol
        board = [symbol_map.get(char, ' ') for char in status]

        # Format and print the board in a 3x3 grid
        rows = [
            board[0:3],  # First row
            board[3:6],  # Second row
            board[6:9]  # Third row
        ]

        # Display the formatted board
        for i, row in enumerate(rows):
            print(" " + " | ".join(row))
            if i < 2:
                print("---+---+---")

        # Display turn information based on client's turn status
        if client.in_turn and (client.is_player or client.owner):
            print("Your opponent's turn.")
            client.in_turn = False
        elif not client.in_turn and (client.is_player or client.owner):
            print("It's your turn.")
            client.in_turn = True

    def process_response(self, conn, parts, server):
        """
        Processes the response from the server. This action does not modify
        connection or server state.

        Args:
            conn (socket): The connection object to the server.
            parts (list): The parsed parts of the protocol message.
            server (object): The server instance handling the game.
        """
