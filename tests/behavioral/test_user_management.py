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

    admin = test_user_management.users[0]
    admin.set_user_action(UserAction.ADMINISTRATION)

    await admin.send_message("Управление пользователями")

    expected = "Управление пользователями"
    admin.expect_answer(expected)
    admin.expect_no_more_answers()
    admin.assert_user_action(UserAction.ADMIN_USER_MANAGEMENT)
