import enum
from dataclasses import dataclass
from typing import Optional

class UserAction(enum.Enum):
    awaiting_authz = 1  # await authorization
    choosing_plan = 2
    training = 3
    administration = 4
    admin_removing_excercise_name = 5
    admin_removing_excercise_prove = 6
    admin_adding_excercise_name = 7
    admin_adding_excercise_link = 8
    admin_adding_excercise_prove = 9


@dataclass
class RemoveExcerciseLinkContext:
    name: str = ""


@dataclass
class AddExcerciseLinkContext:
    name: str = ""
    link: str = ""


@dataclass
class UserContext:
    current_table_id: Optional[str] = None
    current_page: Optional[str] = None
    current_week: Optional[int] = None
    current_workout: Optional[int] = None
    action: UserAction = UserAction.awaiting_authz
    # permissions
    administrative_permission: bool = False
    # additional stored user input, may be anything
    user_input_data: 'typing.Any' = None


class Users:
    # map user_id -> UserContext
    __users = {}

    def get_user_context(self, user_id):
        """
        Returns UserContext for telegram user_id. If UserContext not present,
        creates new one.
        """

        if user_id not in self.__users:
            self.__users[user_id] = UserContext()
        return self.__users[user_id]

    def set_administrative_permission(self, user_id):
        user_context = self.get_user_context(user_id)
        user_context.administrative_permission = True
        user_context.action = UserAction.administration
        user_context.data = ""

    def get_unique_users(self):
        """
        Returns number of unique users
        """

        return len(self.__users)
