"""
Prints all users from DataModel.
"""

import sys
from data_model.users import Users
from view.users import user_to_text_message


if __name__ == "__main__":
    # users_data_filename = sys.argv[1]
    #
    # users = Users(users_data_filename)
    #
    # for user in users.get_all_users():
    #     print(f"id: {user.user_id} - {user_to_text_message(user)}, action: {user.action}, week: {user.current_week}")


    # merge users
    users_ya = Users("secrets/data/2022-10-21/production/users_storage")
    users_ma = Users("secrets/data/2022-10-21/production_mail/production/secrets/users_storage")
    users_res = Users("secrets/data/2022-10-21/merged/users_storage")

    yandex_users = users_ya.get_all_users()
    mail_users = users_ma.get_all_users()

    for user in yandex_users:
        if user.user_id != 129931780:
            users_res.set_user_context(user)
            print(f"id: {user.user_id} - {user_to_text_message(user)}, action: {user.action}, week: {user.current_week}")

    for user in mail_users:
        if user.user_id in (129931780, 352245910, 179154105):
            print(f"id: {user.user_id} - {user_to_text_message(user)}, action: {user.action}, week: {user.current_week}")
            users_res.set_user_context(user)
