"""
Tests related to user authorization.
"""

from workout_bot.data_model.users import UserAction
from workout_bot.view.utils import escape_text


async def test_not_private_chat(behavioral_test_fixture):
    """
    Given: Alice not authorized.
    When: Alice starts bot not in private chat.
    Then: Message that bot can be started only in private chat is shown.
    """

    alice = behavioral_test_fixture.add_user()
    alice.chat_with_bot.type = "public"

    # starts bot
    await alice.send_message("/start")

    # she gets an answer about authorization
    alice.expect_answer("Бот доступен только в приватном чате")
    alice.expect_no_more_answers()


async def test_unauthorized(behavioral_test_fixture):
    """
    Given: Alice not authorized.
    When: Alice starts bot.
    Then: Alice is asked to wait for authorization.
    """

    # When an unauthorized user
    alice = behavioral_test_fixture.add_user()

    # starts bot
    await alice.send_message("/start")

    # she gets an answer about authorization
    alice.expect_answer("Ожидайте подтверждения авторизации")
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.AWAITING_AUTHORIZATION)


async def test_blocked(behavioral_test_fixture):
    """
    Given: Alice is blocked.
    When: Alice sends a message.
    Then: Alice is answered that she is blocked.
    """

    # When a blocked user
    alice = behavioral_test_fixture.add_user()
    behavioral_test_fixture.data_model.users.block_user(alice.user.id)

    # sends a message
    await alice.send_message("hello")

    # she gets message she is blocked
    alice.expect_answer("Вы заблокированы.")
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.BLOCKED)


async def test_blocked_start(behavioral_test_fixture):
    """
    Given: Alice is blocked.
    When: Alice sends start command.
    Then: Alice is answered that she is blocked.
    """

    # When a blocked user
    alice = behavioral_test_fixture.add_user()
    behavioral_test_fixture.data_model.users.block_user(alice.user.id)

    # sends /start command
    await alice.send_message("/start")

    # she gets message she is blocked
    alice.expect_answer("Вы заблокированы.")
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.BLOCKED)


async def test_admin_authorizes_user(test_with_workout_tables):
    """
    Given: User Alice is waiting for authorization.
    When: Admin Bob authorizes Alice and assignes her a table.
    Then: Alice is notified and can choose plan.
    """

    # Alice is a user
    alice = test_with_workout_tables.add_user()

    # Bob is an admin
    bob = test_with_workout_tables.add_admin()
    bob.set_user_action(UserAction.ADMIN_USER_AUTHORIZATION)

    # There is a workout table
    table_name = test_with_workout_tables.workout_tables[0].table_name

    # Alice starts the bot
    await alice.send_message("/start")
    alice.expect_answer("Ожидайте подтверждения авторизации")
    alice.expect_no_more_answers()

    # Bob authorizes Alice
    await bob.send_message(f"Авторизовать id: {alice.user.id}")
    # and assignes a table
    await bob.send_message(table_name)

    # Alice is notified
    table_name = escape_text(table_name)
    expected = f"Назначена программа тренировок *{table_name}*\n\n"
    expected += "Для продолжения нажмите \"Перейти к тренировкам\""
    alice.expect_answer(expected)
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.CHOOSING_PLAN)


async def test_admin_cancels_user_authorization(test_with_workout_tables):
    """
    Given: Bob is an admin and authorizing users.
    When: Bob sends cancel.
    Then: Bob in user management state.
    """

    # Bob is an admin
    bob = test_with_workout_tables.add_admin()
    bob.set_user_action(UserAction.ADMIN_USER_AUTHORIZATION)

    await bob.send_message("Отмена")

    bob.expect_answer("Управление пользователями")
    bob.expect_no_more_answers()
    bob.assert_user_action(UserAction.ADMIN_USER_MANAGEMENT)
