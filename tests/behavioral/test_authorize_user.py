"""
Tests related to user authorization.
"""

def test_unauthorized(behavioral_test_fixture):
    """
    Given: Alice not authorized.
    When: Alice starts bot.
    Then: Alice is asked to wait for authorization.
    """

    # When an unathorized user
    alice = behavioral_test_fixture.add_user("Alice", "Liddell", "wondergirl")

    # starts bot
    alice.send_message("/start")

    # she gets an answer about authorization
    alice.expect_answer("Ожидайте подтверждения авторизации")
    alice.expect_no_more_answers()
