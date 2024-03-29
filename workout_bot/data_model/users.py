"""
Provides access to user data.
"""

import enum
import shelve
from dataclasses import dataclass
from typing import Any
from typing import Optional


class UserAction(enum.IntEnum):
    """
    Current user state. What the user is doing right now.
    """

    BLOCKED = 0
    AWAITING_AUTHORIZATION = 1
    CHOOSING_PLAN = 2
    TRAINING = 3
    ADMINISTRATION = 4
    ADMIN_TABLE_MANAGEMENT = 5
    ADMIN_ADDING_TABLE = 6
    ADMIN_USER_MANAGEMENT = 7
    ADMIN_USER_AUTHORIZATION = 8
    ADMIN_USER_BLOCKING = 9
    ADMIN_USER_ASSIGNING_TABLE = 10
    ADMIN_ADDING_ADMIN = 11
    USER_NEEDS_PROGRAM = 12


@dataclass
class BlockUserContext:
    """
    Stores user_id when the admin is blocking the user.
    """

    user_id: int


@dataclass
class AssignTableUserContext:
    """
    Stores user_id when the admin is assigning a new plan to the user.
    """

    user_id: int


@dataclass
class UserContext:
    """
    Stores all the data related to user.
    """

    # pylint: disable=too-many-instance-attributes

    user_id: int = 0
    first_name: str = ""
    last_name: str = ""
    username: str = ""
    # private chat with user
    chat_id: int = 0
    current_table_id: Optional[str] = None
    current_page: Optional[str] = None
    current_week: Optional[int] = None
    current_workout: Optional[int] = None
    action: UserAction = UserAction.AWAITING_AUTHORIZATION
    # permissions
    administrative_permission: bool = False
    # additional stored user input, may be anything
    user_input_data: Any = None

    def __hash__(self):
        return self.user_id


class Users:
    """
    Provides methods for the user data manipulation.
    """

    def __init__(self, filename):
        """
        Sets shelve storage filename.
        """
        # map user_id -> UserContext
        self.__users = {}

        self.__storage_filename = filename
        self.__users = shelve.open(self.__storage_filename, writeback=True)

    def get_all_users(self):
        """
        Returns all user contexts
        """

        return set(self.__users.values())

    def is_present(self, user_id):
        """
        Returns True if user is present.
        """

        return str(user_id) in self.__users

    def set_user_context(self, user_context):
        """
        Stores user_context.
        """

        self.__users[str(user_context.user_id)] = user_context
        self.__users.sync()

    def get_user_context(self, user_id):
        """
        Returns UserContext for user_id or None if user_id is unknown.
        """

        if str(user_id) not in self.__users:
            return None
        return self.__users[str(user_id)]

    def get_user_context_by_username(self, username):
        """
        Returns user contexts by user_id if user_id is present. Otherwise,
        returns None.
        """

        if username.startswith('@'):
            username = username[1:]
        for user in self.__users.values():
            if username == user.username:
                return user
        return None

    def get_user_context_by_short_username(self, short_username):
        """
        Returns user_context from short username.
        Short username either telegram username starting with `@`,
        either telegram user id starting with `id:`.
        """

        if short_username.startswith('@'):
            return self.get_user_context_by_username(short_username)
        if short_username.startswith("id: "):
            try:
                return self.get_user_context(int(short_username[4:]))
            except ValueError:
                return None
        return None

    def get_or_create_user_context(self, user_id):
        """
        Returns UserContext for telegram user_id. If UserContext not present,
        creates new one.
        """

        if str(user_id) not in self.__users:
            self.__users[str(user_id)] = UserContext(user_id=user_id)
            self.__users.sync()
        return self.__users[str(user_id)]

    def set_user_action(self, user_id, action):
        """
        Sets action for user_id. If user_id is not present, creates a new one.
        """

        user_context = self.get_or_create_user_context(user_id)
        user_context.action = action
        self.__users.sync()

    def is_user_awaiting_authorization(self, user_id):
        """
        If user is present and user action status is AWAITING_AUTHORIZATION.
        """

        user_context = self.get_or_create_user_context(user_id)
        return user_context.action == UserAction.AWAITING_AUTHORIZATION

    def is_user_blocked(self, user_id):
        """
        If user is present and user action status is BLOCKED.
        """

        user_context = self.get_or_create_user_context(user_id)
        return user_context.action == UserAction.BLOCKED

    def set_table_for_user(self, user_id, table_id):
        """
        Sets table for user_id. If user_id is not present, creates a new one.
        """

        user_context = self.get_or_create_user_context(user_id)
        user_context.current_table_id = table_id
        self.__users.sync()

    def set_page_for_user(self, user_id, page):
        """
        Sets page for user_id. If user_id is not present, creates a new one.
        """

        user_context = self.get_or_create_user_context(user_id)
        user_context.current_page = page
        self.__users.sync()

    def set_administrative_permission(self, user_id):
        """
        Sets administrative_permission for user_id. If user_id is not present,
        creates a new one.
        """

        user_context = self.get_or_create_user_context(user_id)
        user_context.administrative_permission = True
        user_context.action = UserAction.ADMINISTRATION
        user_context.user_input_data = None
        self.__users.sync()

    def set_user_input_data(self, user_id, data):
        """
        Sets user data stored between messages. Depends on user action.
        """

        user_context = self.get_or_create_user_context(user_id)
        user_context.user_input_data = data
        self.__users.sync()

    def block_user(self, user_id):
        """
        Sets blocked action for user_id. If user_id is not present, creates a
        new one.
        """
        user_context = self.get_or_create_user_context(user_id)
        user_context.action = UserAction.BLOCKED
        self.__users.sync()

    def get_users_number(self):
        """
        Returns number of unique users
        """

        return len(self.__users)

    def get_users_awaiting_authorization(self):
        """
        Returns the set of users awaiting authorization.
        """

        result = set()
        for user in self.__users.values():
            if user.action is UserAction.AWAITING_AUTHORIZATION:
                result.add(user)
        return result

    def get_potential_admins(self):
        """
        Returns set of users without admin permissions and not blocked.
        """

        result = set()
        for user in self.__users.values():
            if (user.action is not UserAction.BLOCKED
                    and not user.administrative_permission):
                result.add(user)
        return result
