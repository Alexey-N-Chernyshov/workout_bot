"""
Tests related to user authorization.
"""


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
    await alice.send_message("\\start")

    # she gets message she is blocked
    alice.expect_answer("Вы заблокированы.")
    alice.expect_no_more_answers()
    behavioral_test_fixture.data_model.users.is_user_blocked(alice.user.id)
