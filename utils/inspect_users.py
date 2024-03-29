"""
Prints all users from DataModel.
"""

import sys
from workout_bot.data_model.users import Users
from workout_bot.view.users import user_to_text_message


def main():
    """
    Displays users in the file.
    """

    users_data_filename = sys.argv[1]

    users = Users(users_data_filename)

    for user in users.get_all_users():
        print(f"id: {user.user_id} - {user_to_text_message(user)}",
              f", action: {user.action}, week: {user.current_week}",
              f", user input data present: {user.user_input_data is not None}")


if __name__ == "__main__":
    main()
