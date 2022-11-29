"""
Prints all users from DataModel.
"""

import sys
from data_model.users import Users
from view.users import user_to_text_message


if __name__ == "__main__":
    users_data_filename = sys.argv[1]

    users = Users(users_data_filename)

    for user in users.get_all_users():
        print(f"id: {user.user_id} - {user_to_text_message(user)}",
              f", action: {user.action}, week: {user.current_week}",
              f", data present: {user.user_input_data is not None}")
