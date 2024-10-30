"""
GameEndAction Module

This module defines the GameEndAction class, which handles the end-of-game scenarios in a
Tic-Tac-Toe match. It constructs protocol messages, processes server responses, and displays
the game result to the client.
"""

from actions.action_game import Action


class GameEndAction(Action):
    """
    Handles the GAMEEND action, providing end-of-game feedback to the client based on
    the game result. The GameEndAction class interprets the server's response message
    and displays an appropriate message for the client, such as victory, loss, draw,
    or win due to forfeit.

    Methods:
        construct_protocol_message: Constructs the protocol message for ending the game.
        to_client_stdout: Outputs the game result to the client's standard output.
        process_response: Placeholder method for processing server responses.
    """

    def construct_protocol_message(self) -> str:
        """
        Constructs the protocol message for game end notification.

        Returns:
            str: An empty string as no specific protocol message is needed to end the game.
        """
        return ""

    def to_client_stdout(self, response: str, client) -> None:
        """
        Outputs the game result to the client's standard output based on the server response.

        Args:
            response (str): The protocol response message containing game result information.
            client (object): The client instance, used to determine if the client was a player.

        Game End Scenarios:
            - "0": The specified player has won.
            - "1": The game ended in a draw.
            - "2": The specified player won due to the opponent forfeiting.
        """
        parts = Action.filter_protocol_message(response)
        if parts[2] == "0":
            if parts[3] == client.name and (client.is_player or client.owner):
                print("Congratulations, you won!")
            elif parts[3] != client.name and (client.is_player or client.owner):
                print("Sorry, you lost. Good luck next time.")
            else:
                print(f"{parts[3]} has won this game.")
        elif parts[2] == "1":
            print("The game ended in a draw.")
        elif parts[2] == "2":
            print(f"{parts[3]} won due to the opposing player forfeiting.")
        client.after_game()

    def process_response(self, conn, parts, server):
        """
        Processes the response from the server. This action does not modify
        connection or server state.

        Args:
            conn (socket): The connection object to the server.
            parts (list): The parsed parts of the protocol message.
            server (object): The server instance handling the game.
        """
