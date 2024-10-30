"""
Module for Action Management in a Game System

This module defines a factory function and helper functions to manage different
actions in a game system. Each action corresponds to a specific user command, such
as logging in, registering, joining a room, or making a move in the game. Actions
are created using a factory pattern based on action type strings.

Global Variables:
    username (str): Stores the username of the currently authenticated user.
    roomname (str): Stores the name of the room the user has joined or created.
    roleroom (str): Stores the user's role in the room (e.g., "PLAYER" or "VIEWER").
    mode (str): Stores additional mode information related to the room list.

Functions:
    action_factory(action: str) -> Action:
        Creates and returns an instance of the appropriate Action subclass based on the action type.

    save_global_variable(action_instance: Action) -> None:
        Saves session-related data from the given action instance to global variables.

    get_global_variable(action_instance: Action) -> None:
        Retrieves session-related data from global variables
        and assigns it to the given action instance.

Imports:
    Action, BadAction, BeginAction, BoardStatusAction, GameEndAction, InprogressAction,
    CreateRoomAction, JoinAction, LoginAction, RegisterAction,
    RoomListAction, PlayAction, QuitAction

This module helps manage the game flow by storing and retrieving session data across different
actions, enabling continuity of user experience across interactions.
"""

from actions.action_game import Action
from actions.bad_action import BadAction
from actions.game.begin_action import BeginAction
from actions.game.board_status_action import BoardStatusAction
from actions.game.game_end_action import GameEndAction
from actions.game.inprogress_action import InprogressAction
from actions.room.create_room import CreateRoomAction
from actions.room.join_action import JoinAction
from actions.auth.login_action import LoginAction
from actions.auth.register_action import RegisterAction
from actions.room.room_list_action import RoomListAction
from actions.game.play_action import PlayAction
from actions.game.quit_action import QuitAction

# Global variables to store session-related information
username, roomname, roleroom, mode = None, None, None, None


def action_factory(action: str) -> Action:
    """
    Factory function to create instances of Action subclasses based on the action type.

    Args:
        action (str): The type of action to be performed (e.g., "LOGIN", "REGISTER").

    Returns:
        Action: An instance of the corresponding action class (e.g., LoginAction, RegisterAction).
                If the action type is unrecognized, it returns an instance of BadAction.

    Action Mappings:
        - "LOGIN" -> LoginAction
        - "REGISTER" -> RegisterAction
        - "ROOMLIST" -> RoomListAction
        - "CREATE" -> CreateRoomAction
        - "JOIN" -> JoinAction
        - "PLACE" -> PlayAction
        - "FORFEIT" -> QuitAction
        - "BEGIN" -> BeginAction
        - "INPROGRESS" -> InprogressAction
        - "BOARDSTATUS" -> BoardStatusAction
        - "GAMEEND" -> GameEndAction
    """
    action_map = {
        "LOGIN": LoginAction,
        "REGISTER": RegisterAction,
        "ROOMLIST": RoomListAction,
        "CREATE": CreateRoomAction,
        "JOIN": JoinAction,
        "PLACE": PlayAction,
        "FORFEIT": QuitAction,
        "BEGIN": BeginAction,
        "INPROGRESS": InprogressAction,
        "BOARDSTATUS": BoardStatusAction,
        "GAMEEND": GameEndAction
    }
    return action_map.get(action, BadAction)()


def save_global_variable(action_instance):
    """
    Saves session-related data to global variables based on the type of action.

    Args:
        action_instance (Action): The action instance from which to retrieve and store data.

    This function updates global variables (`username`, `roomname`, `roleroom`, `mode`)
    based on the attributes of the action instance, allowing for persistence of session
    data across different actions.

    Data Mappings:
        - LoginAction -> `username`
        - RegisterAction -> `username`
        - CreateRoomAction -> `roomname`
        - JoinAction -> `roomname`, `roleroom`
        - RoomListAction -> `mode`
    """
    global username, roomname, roleroom, mode

    if isinstance(action_instance, LoginAction):
        username = action_instance.username
    elif isinstance(action_instance, RegisterAction):
        username = action_instance.username
    elif isinstance(action_instance, CreateRoomAction):
        roomname = action_instance.name
    elif isinstance(action_instance, JoinAction):
        roomname = action_instance.room_name
        roleroom = action_instance.mode
    elif isinstance(action_instance, RoomListAction):
        mode = action_instance.mode


def get_global_variable(action_instance):
    """
    Retrieves and assigns session-related data from global variables to an action instance.

    Args:
        action_instance (Action): The action instance to which session data should be assigned.

    This function updates the attributes of the action instance (`action_instance`) with
    data stored in global variables, allowing continuity of user state across different actions.

    Data Mappings:
        - LoginAction -> `username`
        - RegisterAction -> `username`
        - CreateRoomAction -> `roomname`
        - JoinAction -> `roomname`, `roleroom`
        - RoomListAction -> `mode`
    """
    if isinstance(action_instance, LoginAction):
        action_instance.username = username
    elif isinstance(action_instance, RegisterAction):
        action_instance.username = username
    elif isinstance(action_instance, CreateRoomAction):
        action_instance.name = roomname
    elif isinstance(action_instance, JoinAction):
        action_instance.room_name = roomname
        action_instance.mode = roleroom
    elif isinstance(action_instance, RoomListAction):
        action_instance.mode = mode
