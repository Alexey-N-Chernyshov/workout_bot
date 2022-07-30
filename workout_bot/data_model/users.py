import enum
from dataclasses import dataclass, field
from typing import Any
from typing import Optional
from typing import List


class UserAction(enum.Enum):
    blocked = 0
    awaiting_authorization = 1
    choosing_plan = 2
    training = 3
    administration = 4
    admin_removing_excercise_name = 5
    admin_removing_excercise_prove = 6
    admin_adding_excercise_name = 7
    admin_adding_excercise_link = 8
    admin_adding_excercise_prove = 9
    admin_table_management = 10
    admin_removing_table = 11
    admin_adding_table = 12
    admin_removing_pages = 13
    admin_adding_pages = 14
    admin_user_management = 15
    admin_user_authorization = 16
    admin_user_blocking = 17
    admin_user_assigning_table = 18
    admin_adding_admin = 19


@dataclass
class RemoveTableContext:
    table_id: str = ""
    pages: List[str] = field(default_factory=list)


@dataclass
class AddTableContext:
    table_id: str = ""
    pages: List[str] = field(default_factory=list)


@dataclass
class RemoveExcerciseLinkContext:
    name: str = ""


@dataclass
class AddExcerciseLinkContext:
    name: str = ""
    link: str = ""


@dataclass
class BlockUserContext:
    user_id: int

@dataclass
class AssignTableUserContext:
    user_id: int

@dataclass
class UserContext:
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
    action: UserAction = UserAction.awaiting_authorization
    # permissions
    administrative_permission: bool = False
    # additional stored user input, may be anything
    user_input_data: Any = None

    def __hash__(self):
        return self.user_id


class Users:
    # map user_id -> UserContext
    __users = {}

    def get_all_users(self):
        return set(self.__users.values())

    def set_user_context(self, user_context):
        self.__users[user_context.user_id] = user_context

    def get_user_context(self, user_id):
        """
        Returns UserContext for user_id or None if user_id is unknow.
        """

        if user_id not in self.__users:
            return None
        return self.__users[user_id]

    def get_user_context_by_username(self, username):
        if username.startswith('@'):
            username = username[1:]
        for user in self.__users.values():
            if username == user.username:
                return user
        return None

    def get_or_create_user_context(self, user_id):
        """
        Returns UserContext for telegram user_id. If UserContext not present,
        creates new one.
        """

        if user_id not in self.__users:
            self.__users[user_id] = UserContext(user_id=user_id)
        return self.__users[user_id]

    def set_user_action(self, user_id, action):
        user_context = self.get_or_create_user_context(user_id)
        user_context.action = action

    def set_table_for_user(self, user_id, table_id):
        user_context = self.get_or_create_user_context(user_id)
        user_context.current_table_id = table_id

    def set_administrative_permission(self, user_id):
        user_context = self.get_or_create_user_context(user_id)
        user_context.administrative_permission = True
        user_context.action = UserAction.administration
        user_context.user_input_data = None

    def block_user(self, user_id):
        user_context = self.get_or_create_user_context(user_id)
        user_context.action = UserAction.blocked

    def get_users_number(self):
        """
        Returns number of unique users
        """

        return len(self.__users)

    def get_users_awaiting_authorization(self):
        result = set()
        for user in self.__users.values():
            if user.action == UserAction.awaiting_authorization:
                result.add(user)
        return result

    def get_potential_admins(self):
        """
        Returns set of users without admin permissions and not blocked.
        """

        result = set()
        for user in self.__users.values():
            if (not user.action == UserAction.blocked
                    and not user.administrative_permission):
                result.add(user)
        return result
