"""
Utitlity scripts for project.
"""

from data_model.users import Users


def print_all_users(filename):
    """
    Prints all users from data model.
    """

    users = Users(filename)

    for user in users.get_all_users():
        print(user)


print_all_users("secrets/users_storage")
