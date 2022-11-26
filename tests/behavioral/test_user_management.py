"""
Behavioral tests for user management.
"""

from workout_bot.data_model.users import UserAction


async def test_go_user_management(test_user_management):
    """
    Given: admin in ADMINISTRATION state.
    When: admin sends go to user management.
    Then: admin is in ADMIN_USER_MANAGEMENT state and user management panel is
    sent.
    """

    admin = test_user_management.admin
    admin.set_user_action(UserAction.ADMINISTRATION)

    await admin.send_message("Управление пользователями")

    expected = "Управление пользователями"
    admin.expect_answer(expected)
    admin.expect_no_more_answers()
    admin.assert_user_action(UserAction.ADMIN_USER_MANAGEMENT)


async def test_show_all_users(test_user_management):
    """
    Given: admin in ADMIN_USER_MANAGEMENT state.
    When: admin sends show all users message.
    Then: admin is shown all users.
    """

    admin = test_user_management.admin

    await admin.send_message("Показать всех")

    table = test_user_management.table_name
    expected = "Ожидают авторизации:\n"
    expected += " \\- @waiting\n"
    expected += "\n"
    expected += "Тренируются:\n"
    expected += f" \\- @admin \\- {table} \\- администратор\n"
    expected += f" \\- @user \\- {table}\n"
    expected += "\n"
    expected += "Заблокрироанные:\n"
    expected += " \\- @blocked\n"
    admin.expect_answer(expected)
    admin.expect_no_more_answers()
