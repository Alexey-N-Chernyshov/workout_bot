"""
Test bot handlers related to administration.
"""

from workout_bot.data_model.users import UserAction
from workout_bot.view.workouts import get_workout_text_message


async def test_go_to_training(test_with_workout_tables):
    """
    Given: Alice is admin and in ADMINISTRATION state.
    When: Alice sends go to training.
    Then: Workout is sent and she is TRAINING.
    """

    alice = test_with_workout_tables.add_admin()
    alice.set_user_action(UserAction.ADMINISTRATION)
    table = test_with_workout_tables.workout_tables[0]
    plan = test_with_workout_tables.get_table_plan(table, 0)
    alice.set_table(table.table_id)
    alice.set_page(plan)

    # sends a message
    await alice.send_message("Перейти к тренировкам")

    # she gets message with workout
    expected = get_workout_text_message(
        test_with_workout_tables.data_model,
        table.table_id,
        plan,
        0,
        0
    )
    alice.expect_answer(expected)
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.TRAINING)
