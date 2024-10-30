"""
PlayAction Module

This module defines the PlayAction class and supporting functions to handle the process of
a player making a move in a Tic-Tac-Toe game. It checks room membership, validates moves,
updates game status, and manages the end-of-game responses.

Classes:
    PlayAction: Represents the action of a player placing a marker on the board.

Functions:
    check_join_room: Verifies if a player is in an active room.
    check_all_characters_not_zero: Checks if all positions on the board are filled.
    check_status: Determines if there is a winner based on the board status.
    handle_response_game_end: Manages end-of-game responses, sending messages to players
                              and viewers, and cleaning up the room.
    play_game: Executes the player’s move, updates the board, and checks game state.
"""

from actions.action_game import Action


def check_join_room(conn, server):
    """
    Checks if the player associated with the connection is currently in a room.

    Args:
        conn: The connection object of the player.
        server: The server instance with authenticated users and rooms.

    Returns:
        bool: True if the player is in a room, False otherwise.
    """
    if server.authenticated_users[conn] in server.rooms_dict:
        return True
    return False


def check_all_characters_not_zero(input_string):
    """
    Checks if all characters in a string are non-zero, indicating the board is full.

    Args:
        input_string (str): The string to check, typically representing the board status.

    Returns:
        bool: True if all characters are non-zero, False otherwise.
    """
    for char in input_string:
        if char == '0':
            return False
    return True


def check_status(board_status):
    """
    Determines if there is a winner based on the current board status.

    Args:
        board_status (str): A 9-character string representing the Tic-Tac-Toe board.

    Returns:
        str: "1" if player X wins, "2" if player O wins, or "0" if no winner.
    """
    if board_status[0] == board_status[1] and board_status[1] == board_status[2]:
        return board_status[0]
    if board_status[0] == board_status[3] and board_status[3] == board_status[6]:
        return board_status[0]
    if board_status[0] == board_status[4] and board_status[4] == board_status[8]:
        return board_status[0]
    if board_status[1] == board_status[4] and board_status[4] == board_status[7]:
        return board_status[1]
    if board_status[2] == board_status[5] and board_status[5] == board_status[8]:
        return board_status[2]
    if board_status[2] == board_status[4] and board_status[4] == board_status[6]:
        return board_status[2]
    return "0"


def handle_response_game_end(room, server, message):
    """
    Sends a game end message to players and viewers, and updates the server state by removing
    the room.

    Args:
        room (Room): The game room instance.
        server: The server instance with room information.
        message (str): The message to send to clients indicating the game has ended.
    """
    x_player_conn = room.x_player
    y_player_conn = room.y_player
    x_player_conn.sendall(f"{message}\n".encode('ascii'))
    if y_player_conn is not None:
        y_player_conn.sendall(f"{message}\n".encode('ascii'))
    for viewer in room.viewer:
        viewer.sendall(f"{message}\n".encode('ascii'))

    owner = server.authenticated_users[x_player_conn]
    del server.rooms_dict[owner]
    del server.rooms[room.name]


def play_game(conn, room, position):
    """
    Executes a move on the board and updates the game state.

    Args:
        conn: The player connection making the move.
        room (Room): The game room instance.
        position (int): The position index on the board to place the move.

    Returns:
        str: Status message indicating game continuation or end.
    """
    x_player_conn = room.x_player
    y_player_conn = room.y_player

    if room.board_status[position] != "0":
        return ""

    value = "1" if room.x_player == conn else "2"
    string_list = list(room.board_status)
    string_list[position] = value
    room.board_status = "".join(string_list)

    if check_all_characters_not_zero(room.board_status):
        return "GAMEEND1"

    game_check = check_status(room.board_status)
    if game_check != "0":
        return "GAMEEND0"
    elif room.started:
        room.current_turn = x_player_conn if y_player_conn == conn else y_player_conn
        room.opposing_turn = x_player_conn if x_player_conn == conn else y_player_conn
        return "PLAYGAME"


class PlayAction(Action):
    """
    Represents an action for placing a move on the Tic-Tac-Toe board.

    Methods:
        construct_protocol_message: Prompts for and constructs a move placement message.
        to_client_stdout: No action is required for this method.
        handle_play_game: Executes the move, checks the game state, and updates the board.
        process_response: Processes the server-side response to validate and update the game.
    """

    def __init__(self):
        """
        Initializes a PlayAction instance. Inherits the structure of an Action but
        provides no additional attributes or properties.
        """
        super().__init__()

    def construct_protocol_message(self) -> str:
        """
        Prompts for the X and Y coordinates to place a marker on the board.

        Returns:
            str: A formatted string in the form "PLACE:x:y" representing the move coordinates.
        """
        x_verified = False
        while True:
            if not x_verified:
                x = int(input("Enter x position:"))
                if x < 0 or x > 2:
                    print(f"Error: Column values must be an integer between 0 and 2")
                    continue
                x_verified = True
            y = int(input("Enter y position:"))
            if y < 0 or y > 2:
                print(f"Error: Row values must be an integer between 0 and 2")
                continue
            return f"PLACE:{x}:{y}"

    def to_client_stdout(self, response: str, client) -> None:
        """
        Placeholder method; no specific client output handling for PlayAction.

        Args:
            response (str): The server's response message.
            client: The client instance.
        """

    def handle_play_game(self, room, conn, server, position):
        """
        Manages the gameplay by executing moves, updating the board, and checking game status.

        Args:
            room (Room): The current game room.
            conn: The connection of the player making the move.
            server: The server instance with room data.
            position (int): The board position to place the move.
        """
        cur_queue = room.x_player_queue if conn == room.x_player else room.y_player_queue
        if room.current_turn == conn:
            if not room.started:
                cur_queue.append(position)
                return
            if len(cur_queue) > 0:
                position = cur_queue.pop(0)
            if position is None:
                return
        else:
            cur_queue.append(position)
            return

        if position is None:
            return
        match_status = play_game(conn, room, position)
        if match_status == "GAMEEND0":
            username = server.authenticated_users[conn]
            message = f"GAMEEND:{room.board_status}:0:{username}"
            handle_response_game_end(room, server, message)
            return
        elif match_status == "GAMEEND1":
            message = f"GAMEEND:{room.board_status}:1"
            handle_response_game_end(room, server, message)
            return
        else:
            if room.started:
                x_player_conn = room.x_player
                y_player_conn = room.y_player
                x_player_conn.sendall(f"BOARDSTATUS:{room.board_status}\n".encode('ascii'))
                if y_player_conn is not None:
                    y_player_conn.sendall(f"BOARDSTATUS:{room.board_status}\n".encode('ascii'))
                for viewer in room.viewer:
                    viewer.sendall(f"BOARDSTATUS:{room.board_status}\n".encode('ascii'))
                self.handle_play_game(room, room.current_turn, server, None)

    def process_response(self, conn, parts, server):
        """
        Processes the client's move request, validates it, and updates the server's game state.

        Args:
            conn: The client connection making the move request.
            parts (list): Parsed parts of the move message.
            server: The server instance to manage game state.
        """
        if conn not in server.authenticated_users:
            conn.sendall("BADAUTH\n".encode('ascii'))
            return
        if not check_join_room(conn, server):
            conn.sendall("NOROOM\n".encode('ascii'))
            return
        room_name = server.rooms_dict[server.authenticated_users[conn]]
        room = server.rooms[room_name]

        x = int(parts[1])
        y = int(parts[2])
        index = y * 3 + x
        self.handle_play_game(room, conn, server, index)
