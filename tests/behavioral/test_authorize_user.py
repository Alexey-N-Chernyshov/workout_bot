"""
Tests related to user authorization.
"""


from workout_bot.data_model.users import UserAction
from workout_bot.data_model.workout_plans import WorkoutTable


async def test_unauthorized(behavioral_test_fixture):
    """
    Given: Alice not authorized.
    When: Alice starts bot.
    Then: Alice is asked to wait for authorization.
    """

    # When an unathorized user
    alice = behavioral_test_fixture.add_user()

    # starts bot
    await alice.send_message("/start")

    # she gets an answer about authorization
    alice.expect_answer("Ожидайте подтверждения авторизации")
    alice.expect_no_more_answers()
    behavioral_test_fixture.data_model \
        .users.is_user_awaiting_authorization(alice.user.id)


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
    behavioral_test_fixture.data_model.users.is_user_blocked(alice.user.id)


async def test_blocked_start(behavioral_test_fixture):
    """
    Given: Alice is blocked.
    When: Alice sends start command.
    Then: Alice is answered that she is blocked.
    """

    # When a blocked user
    alice = behavioral_test_fixture.add_user()
    behavioral_test_fixture.data_model.users.block_user(alice.user.id)

    # sends start command
    await alice.send_message("/start")

    # she gets message she is blocked
    alice.expect_answer("Вы заблокированы.")
    alice.expect_no_more_answers()
    behavioral_test_fixture.data_model.users.is_user_blocked(alice.user.id)


async def test_admin_authorizes_usesr(behavioral_test_fixture):
    """
    Given: User Alice is waiting for authorization.
    When: Admin Bob authorizes Alice and assignes her a table.
    Then: Alice is notified and can choose plan.
    """

    # Alice is a user
    alice = behavioral_test_fixture.add_user()

    # Bob is an admin
    bob = behavioral_test_fixture.add_user()
    behavioral_test_fixture.data_model \
        .users.set_administrative_permission(bob.user.id)
    behavioral_test_fixture.data_model \
        .users.set_user_action(bob.user.id,
                               UserAction.ADMIN_USER_AUTHORIZATION)

    # There is a workout table
    table_name = "table_name"
    table = WorkoutTable("table_id", table_name, {})
    behavioral_test_fixture.data_model \
        .workout_plans.update_workout_table(table)

    # Alice starts the bot
    await alice.send_message("/start")
    print(behavioral_test_fixture.data_model \
        .users.get_user_context(alice.user.id))
    alice.expect_answer("Ожидайте подтверждения авторизации")
    alice.expect_no_more_answers()

    # Bob authorizes Alice
    await bob.send_message(f"Авторизовать id: {alice.user.id}")
    # and assignes a table
    await bob.send_message(table_name)

    # Alice is notified
    alice.expect_answer(f'Назначена таблица "{table_name}"')
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.CHOOSING_PLAN)
