"""
Tests related to training status.
"""

from workout_bot.data_model.users import UserAction


async def test_start_training_unassigned(behavioral_test_fixture):
    """
    Given: Alice is authorized but no program assigned.
    When: Alice presses /start command.
    Then: She is shown message and her state is USER_NEEDS_PROGRAM.
    """

    alice = behavioral_test_fixture.add_authorized_user()

    # sends a message
    await alice.send_message("/start")

    # she gets message she is not assigned table
    alice.expect_answer("Вам не назначена программа тренировок")
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.USER_NEEDS_PROGRAM)


async def test_start_training_invalid_table(behavioral_test_fixture):
    """
    Given: Alice is authorized and her assigned program doesn't exist.
    When: Alice presses /start command.
    Then: She is shown message and her state is USER_NEEDS_PROGRAM.
    """

    alice = behavioral_test_fixture.add_authorized_user()
    alice.set_table("not exists")

    # sends a message
    await alice.send_message("/start")

    # she gets message she is not assigned table
    alice.expect_answer("Назначенная программа не существует")
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.USER_NEEDS_PROGRAM)


async def test_choose_plan_on_start(test_with_workout_tables):
    """
    Given: Alice is authorized and assigned table.
    When: Alice presses /start command.
    Then: She is asked for plan (pagename).
    """

    # alice is assigned a table
    alice = test_with_workout_tables.add_authorized_user()
    table = test_with_workout_tables.workout_tables[0]
    alice.set_table(table.table_id)

    # sends a message
    await alice.send_message("/start")

    # she gets message she is not assigned table
    alice.expect_answer("Программа тренировок не выбрана")
    alice.expect_answer("Выберите программу из списка:")
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.CHOOSING_PLAN)


async def test_start_training(test_with_workout_tables):
    """
    Given: Alice is authorized and program is assigned.
    When: Alice presses /start command.
    Then: Current page is reset and action is CHOOSING_PLAN.
    """

    alice = test_with_workout_tables.add_authorized_user()
    table = test_with_workout_tables.workout_tables[0]
    alice.set_table(table.table_id)
    plan = next(iter(table.pages))
    alice.set_page(plan)
    alice.set_user_action(UserAction.TRAINING)

    # sends a message
    await alice.send_message("/start")

    # she gets message she is not assigned table
    alice.expect_answer("Программа тренировок не выбрана")
    alice.expect_answer("Выберите программу из списка:")
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.CHOOSING_PLAN)
