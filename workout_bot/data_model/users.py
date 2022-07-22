import enum
from dataclasses import dataclass
from typing import Optional

class UserAction(enum.Enum):
    awaiting_authz = 1  # await authorization
    choosing_plan = 2
    training = 3
    administration = 4
    admin_adding_excercise_name = 5
    admin_adding_excercise_link = 6
    admin_adding_excercise_prove = 7


@dataclass
class UserContext:
    current_plan: Optional[str] = None
    current_week: Optional[int] = None
    current_workout: Optional[int] = None
    action: UserAction = UserAction.awaiting_authz
    # permissions
    administrative_permission: bool = False
    # stored input data
    data: str = ""


class Users:
    # map user_id -> UserContext
    __users = {96539438 : UserContext(action=UserAction.choosing_plan,
                                         administrative_permission=True)}

    def get_user_context(self, user_id):
        """
        Returns UserContext for telegram user_id. If UserContext not present,
        creates new one.
        """

        if user_id not in self.__users:
            self.__users[user_id] = UserContext()
        return self.__users[user_id]

    def get_unique_users(self):
        """
        Returns number of unique users
        """

        return len(self.__users)
