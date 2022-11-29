"""
Test bot handlers related to administration.
"""

from workout_bot.data_model.users import UserAction


async def test_go_to_training(test_with_workout_tables):
    """
    Given: Alice is admin and in ADMINISTRATION state.
    When: Alice sends go to training.
    Then: Workout is sent and she is TRAINING.
    """

    alice = test_with_workout_tables.add_admin()
    alice.set_user_action(UserAction.ADMINISTRATION)
    table = test_with_workout_tables.table1
    plan = list(test_with_workout_tables.table1.pages)[0]
    alice.set_table(table.table_id)
    alice.set_page(plan)

    # sends a message
    await alice.send_message("Перейти к тренировкам")

    # she gets message with workout
    expected = test_with_workout_tables \
        .get_expected_workout_text_message(alice)
    alice.expect_answer(expected)
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.TRAINING)
