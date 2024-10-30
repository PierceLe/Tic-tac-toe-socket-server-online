"""
Room Model Module

This module defines the Room class, which manages information about a game room,
including players, viewers, game status, and the game board.

Classes:
    Room: Manages the state of a Tic-Tac-Toe room, including players, viewers, and game status.
"""


class Room:
    """
    A class representing a game room for Tic-Tac-Toe, handling player assignments,
    viewers, and game state.

    Attributes:
        name (str): The name of the room.
        x_player: The player assigned to 'X'.
        y_player: The player assigned to 'O'.
        viewer (list): List of viewers in the room.
        started (bool): Indicates whether the game has started.
        current_turn: The player whose turn it currently is.
        opposing_turn: The opposing player.
        board_status (str): The current state of the board, represented as a 9-character string.
        x_player_queue (list): Queue for 'X' player actions.
        y_player_queue (list): Queue for 'O' player actions.
    """

    def __init__(self, name: str):
        """
        Initializes a Room with the given name and sets up initial game state.

        Args:
            name (str): The name of the room.
        """
        self.name = name
        self.x_player = None
        self.y_player = None
        self.viewer = []
        self.started = False
        self.current_turn = None
        self.opposing_turn = None
        self.board_status = "000000000"
        self.x_player_queue = []
        self.y_player_queue = []

    def is_full(self) -> bool:
        """
        Checks if the room has two players, indicating it is full.

        Returns:
            bool: True if both player slots are filled, False otherwise.
        """
        return self.x_player is not None and self.y_player is not None

    def assign_x_player(self, x_player):
        """
        Assigns a player to the 'X' position and sets them as the current turn.

        Args:
            x_player: The player to assign to 'X'.
        """
        self.x_player = x_player
        self.current_turn = x_player

    def assign_y_player(self, y_player):
        """
        Assigns a player to the 'O' position and sets them as the opposing turn.

        Args:
            y_player: The player to assign to 'O'.
        """
        self.y_player = y_player
        self.opposing_turn = y_player

    def add_viewer(self, viewer):
        """
        Adds a viewer to the room.

        Args:
            viewer: The viewer to add to the room.
        """
        self.viewer.append(viewer)

    @staticmethod
    def get_viewable_room(rooms: dict) -> list:
        """
        Returns a sorted list of room names that can be viewed.

        Args:
            rooms (dict): Dictionary of room instances.

        Returns:
            list: Sorted list of room names.
        """
        return sorted(list(rooms.keys()))

    @staticmethod
    def get_playable_room(rooms: dict) -> list:
        """
        Returns a list of room names where players can join as players.

        Args:
            rooms (dict): Dictionary of room instances.

        Returns:
            list: List of room names with available player slots.
        """
        return [room for room in rooms.keys() if not rooms[room].is_full()]
