"""
Test commands handlers.
"""


async def test_command_about(behavioral_test_fixture):
    """
    Given: Alice is a user.
    When: Alice sends '/about'.
    Then: Alice is shown about message with version and GitHub link.
    """

    alice = behavioral_test_fixture.add_user()

    await alice.send_message("/about")

    # she gets message with workout
    expected = "*Бот для тренировок*\n"
    expected += "Версия: behavioral_test\n"
    expected += \
        "[Github](https://github\\.com/Alexey\\-N\\-Chernyshov/workout\\_bot)"
    alice.expect_answer(expected)
    alice.expect_no_more_answers()
