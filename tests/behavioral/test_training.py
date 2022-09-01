"""
Tests related to training status.
"""

from workout_bot.data_model.users import UserAction
from workout_bot.view.workouts import (
    get_workout_text_message, get_week_routine_text_message
)


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
    expected = test_with_workout_tables.get_choose_plan_message(table)
    alice.expect_answer(expected)
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
    plan = test_with_workout_tables.get_table_plan(table, 0)
    alice.set_page(plan)
    alice.set_user_action(UserAction.TRAINING)

    # sends a message
    await alice.send_message("/start")

    # she gets message she is not assigned table
    expected = test_with_workout_tables.get_choose_plan_message(table)
    alice.expect_answer(expected)
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.CHOOSING_PLAN)


async def test_change_plan(test_with_workout_tables):
    """
    Given: Alice is authorized and table is assigned and she is CHOOSING_PLAN.
    When: Alice chooses plan.
    Then: Plan is assigned and she is TRAINING and new schedule is displayed.
    """

    alice = test_with_workout_tables.add_authorized_user()
    table = test_with_workout_tables.workout_tables[0]
    alice.set_table(table.table_id)
    plan = test_with_workout_tables.get_table_plan(table, 0)
    alice.set_page(plan)

    new_plan = test_with_workout_tables.get_table_plan(table, 1)

    # sends a message
    await alice.send_message(new_plan)

    # she gets message with workout
    expected = get_week_routine_text_message(
        test_with_workout_tables.data_model,
        table.table_id,
        new_plan,
        0
    )
    alice.expect_answer(expected)
    expected = get_workout_text_message(
        test_with_workout_tables.data_model,
        table.table_id,
        new_plan,
        0,
        0
    )
    alice.expect_answer(expected)
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.TRAINING)


async def test_change_plan_invalid(test_with_workout_tables):
    """
    Given: Alice is authorized and table is assigned and she is CHOOSING_PLAN.
    When: Alice chooses wrong plan.
    Then: Alice is shown message that plan is not valid and she is
    CHOOSING_PLAN again.
    """

    alice = test_with_workout_tables.add_authorized_user()
    table = test_with_workout_tables.workout_tables[0]
    alice.set_table(table.table_id)
    plan = test_with_workout_tables.get_table_plan(table, 0)
    alice.set_page(plan)

    new_plan = "wrong plan"

    # sends a message
    await alice.send_message(new_plan)

    # she gets message no such plan
    alice.expect_answer("Нет такой программы")
    # asks to change plan again
    expected = test_with_workout_tables.get_choose_plan_message(table)
    alice.expect_answer(expected)
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.CHOOSING_PLAN)


async def test_user_changes_plan(test_with_workout_tables):
    """
    Given: Alice is authorized and plan is chosen and she is TRAINING.
    When: Alice sends change plan message.
    Then: Alice is shown message change plan and she is CHOOSING_PLAN.
    """

    alice = test_with_workout_tables.add_authorized_user()
    table = test_with_workout_tables.workout_tables[0]
    alice.set_table(table.table_id)
    plan = test_with_workout_tables.get_table_plan(table, 0)
    alice.set_page(plan)
    alice.set_user_action(UserAction.TRAINING)

    # sends a message
    await alice.send_message("Сменить программу")

    # asks to change plan again
    expected = test_with_workout_tables.get_choose_plan_message(table)
    alice.expect_answer(expected)
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.CHOOSING_PLAN)


async def test_user_changes_plan_no_page(test_with_workout_tables):
    """
    Given: Alice is authorized and plan is not chosen and she is TRAINING.
    When: Alice sends change plan message.
    Then: Alice is shown message change plan and she is CHOOSING_PLAN.
    """

    alice = test_with_workout_tables.add_authorized_user()
    table = test_with_workout_tables.workout_tables[0]
    alice.set_table(table.table_id)
    alice.set_user_action(UserAction.TRAINING)

    # sends any message
    await alice.send_message("Далее")

    # asks to change plan again
    expected = test_with_workout_tables.get_choose_plan_message(table)
    alice.expect_answer(expected)
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.CHOOSING_PLAN)


async def test_training_all_action(test_with_workout_tables):
    """
    Given: Alice is authorized and plan is not chosen and she is TRAINING.
    When: Alice sends show all message.
    Then: Alice is shown message with all actions and she is TRAINING.
    """

    alice = test_with_workout_tables.add_authorized_user()
    table = test_with_workout_tables.workout_tables[0]
    alice.set_table(table.table_id)
    plan = test_with_workout_tables.get_table_plan(table, 0)
    alice.set_page(plan)
    alice.set_user_action(UserAction.TRAINING)

    # sends any message
    await alice.send_message("Все действия")

    # shown all action
    alice.expect_answer("Доступные действия:")
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.TRAINING)


async def test_training_invalid_plan(test_with_workout_tables):
    """
    Given: Alice is authorized and plan is invalid and she is TRAINING.
    When: Alice sends any message
    Then: Alice is asked to change plan and she is CHOOSING_PLAN.
    """

    alice = test_with_workout_tables.add_authorized_user()
    table = test_with_workout_tables.workout_tables[0]
    alice.set_table(table.table_id)
    alice.set_page("invalid page")
    alice.set_user_action(UserAction.TRAINING)

    # sends any message
    await alice.send_message("Далее")

    # shown all action
    expected = test_with_workout_tables.get_choose_plan_message(table)
    alice.expect_answer(expected)
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.CHOOSING_PLAN)


async def test_go_to_training(test_with_user_with_workouts):
    """
    Given: Alice is authorized and table is assigned and she is TRAINING.
    When: Alice sends go to training.
    Then: Workout is sent and she is TRAINING.
    """

    alice = test_with_user_with_workouts.users[0]
    table = test_with_user_with_workouts.workout_tables[0]
    plan = test_with_user_with_workouts.get_table_plan(table, 0)

    # sends a message
    await alice.send_message("Перейти к тренировкам")

    # she gets message with workout
    expected = get_workout_text_message(
        test_with_user_with_workouts.data_model,
        table.table_id,
        plan,
        0,
        0
    )
    alice.expect_answer(expected)
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.TRAINING)


async def test_go_next_workout(test_with_user_with_workouts):
    """
    Given: Alice is authorized and table is assigned and she is TRAINING.
    When: Alice requests next.
    Then: The 2nd workout is sent and she is TRAINING.
    """

    alice = test_with_user_with_workouts.users[0]
    table = test_with_user_with_workouts.workout_tables[0]
    plan = test_with_user_with_workouts.get_table_plan(table, 0)

    # sends a message
    await alice.send_message("Далее")

    # she gets message with workout
    expected = get_workout_text_message(
        test_with_user_with_workouts.data_model,
        table.table_id,
        plan,
        0,
        1
    )
    alice.expect_answer(expected)
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.TRAINING)
    alice_context = alice.get_user_context()
    assert alice_context.current_week == 0
    assert alice_context.current_workout == 1


async def test_go_next_week_workout(test_with_user_with_workouts):
    """
    Given: Alice is authorized and table is assigned and it is the last workout
    in the week and she is TRAINING.
    When: Alice requests next.
    Then: The 2nd week workout is sent and she is TRAINING.
    """

    alice = test_with_user_with_workouts.users[0]
    table = test_with_user_with_workouts.workout_tables[0]
    plan = test_with_user_with_workouts.get_table_plan(table, 0)
    alice.set_workout_number(1)

    # sends a message
    await alice.send_message("Далее")

    # she gets message with new week number 1
    expected = get_week_routine_text_message(
        test_with_user_with_workouts.data_model,
        table.table_id,
        plan,
        1
    )
    alice.expect_answer(expected)
    # and 0 workout of week 1
    expected = get_workout_text_message(
        test_with_user_with_workouts.data_model,
        table.table_id,
        plan,
        1,
        0
    )
    alice.expect_answer(expected)
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.TRAINING)
    alice_context = alice.get_user_context()
    assert alice_context.current_week == 1
    assert alice_context.current_workout == 0


async def test_go_next_last_week_last_workout(test_with_user_with_workouts):
    """
    Given: Alice is authorized and table is assigned and it is the last workout
    in the last week and there is no more weeks and she is TRAINING.
    When: Alice requests next.
    Then: The last workout of last week is sent and she is TRAINING.
    """

    alice = test_with_user_with_workouts.users[0]
    table = test_with_user_with_workouts.workout_tables[0]
    plan = test_with_user_with_workouts.get_table_plan(table, 0)
    # last workout of the last week
    alice.set_week_number(1)
    alice.set_workout_number(1)

    # sends a message
    await alice.send_message("Далее")

    # she gets message with the last workout of the last week
    expected = get_workout_text_message(
        test_with_user_with_workouts.data_model,
        table.table_id,
        plan,
        1,
        1
    )
    alice.expect_answer(expected)
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.TRAINING)
    alice_context = alice.get_user_context()
    assert alice_context.current_week == 1
    assert alice_context.current_workout == 1


async def test_go_first_week(test_with_user_with_workouts):
    """
    Given: Alice is authorized and table is assigned and current week is 2nd
    and current workout is 2nd and she is TRAINING.
    When: Alice goes to the first week.
    Then: The current week is the first and current workout is first and she is
    TRAINING.
    """

    alice = test_with_user_with_workouts.users[0]
    table = test_with_user_with_workouts.workout_tables[0]
    plan = test_with_user_with_workouts.get_table_plan(table, 0)
    # last workout of the last week
    alice.set_week_number(1)
    alice.set_workout_number(1)

    # sends a message
    await alice.send_message("Первая неделя")

    # she gets message with new week number 0
    expected = get_week_routine_text_message(
        test_with_user_with_workouts.data_model,
        table.table_id,
        plan,
        0
    )
    alice.expect_answer(expected)
    # she gets message with the last workout of the last week
    expected = get_workout_text_message(
        test_with_user_with_workouts.data_model,
        table.table_id,
        plan,
        0,
        0
    )
    alice.expect_answer(expected)
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.TRAINING)
    alice_context = alice.get_user_context()
    assert alice_context.current_week == 0
    assert alice_context.current_workout == 0


async def test_go_last_week(test_with_user_with_workouts):
    """
    Given: Alice is authorized and table is assigned and current week is 1nd
    and current workout is 1nd and she is TRAINING.
    When: Alice goes to the last week.
    Then: The current week is the last and current workout is first and she is
    TRAINING.
    """

    alice = test_with_user_with_workouts.users[0]
    table = test_with_user_with_workouts.workout_tables[0]
    plan = test_with_user_with_workouts.get_table_plan(table, 0)
    # last workout of the last week
    alice.set_week_number(0)
    alice.set_workout_number(1)

    # sends a message
    await alice.send_message("Последняя неделя")

    # she gets message with new week number 0
    expected = get_week_routine_text_message(
        test_with_user_with_workouts.data_model,
        table.table_id,
        plan,
        1
    )
    alice.expect_answer(expected)
    # she gets message with the last workout of the last week
    expected = get_workout_text_message(
        test_with_user_with_workouts.data_model,
        table.table_id,
        plan,
        1,
        0
    )
    alice.expect_answer(expected)
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.TRAINING)
    alice_context = alice.get_user_context()
    assert alice_context.current_week == 1
    assert alice_context.current_workout == 0


async def test_go_next_week(test_with_user_with_workouts):
    """
    Given: Alice is authorized and table is assigned and current week is 1nd
    and current workout is 1nd and she is TRAINING.
    When: Alice goes to the next week.
    Then: The current week is the 2nd and current workout is the first and she
    is TRAINING.
    """

    alice = test_with_user_with_workouts.users[0]
    table = test_with_user_with_workouts.workout_tables[0]
    plan = test_with_user_with_workouts.get_table_plan(table, 0)
    # last workout of the last week
    alice.set_week_number(0)
    alice.set_workout_number(1)

    # sends a message
    await alice.send_message("Следующая неделя")

    # she gets message with new week number 0
    expected = get_week_routine_text_message(
        test_with_user_with_workouts.data_model,
        table.table_id,
        plan,
        1
    )
    alice.expect_answer(expected)
    # she gets message with the last workout of the last week
    expected = get_workout_text_message(
        test_with_user_with_workouts.data_model,
        table.table_id,
        plan,
        1,
        0
    )
    alice.expect_answer(expected)
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.TRAINING)
    alice_context = alice.get_user_context()
    assert alice_context.current_week == 1
    assert alice_context.current_workout == 0
