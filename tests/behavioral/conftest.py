"""
Fixtures for behavioral tests.
"""

import datetime
import pytest
from workout_bot.data_model.users import UserAction
from workout_bot.data_model.workout_plans import (
    Workout, WeekRoutine, WorkoutTable
)
from .behavioral_test_fixture import BehavioralTest


def create_workout_table(table_id="table_id", table_name="table_name"):
    """
    Initializes workout table.
    """

    workout1 = Workout("workout1", [], 1, 1)
    workout2 = Workout("workout2", [], 1, 1)
    first_week = WeekRoutine(datetime.date(2022, 8, 29),
                             datetime.date(2022, 9, 4),
                             1,
                             [workout1, workout2],
                             "week one comment")

    second_week = WeekRoutine(datetime.date(2022, 9, 5),
                              datetime.date(2022, 9, 11),
                              1,
                              [workout1, workout2],
                              "week two comment")
    return WorkoutTable(table_id, table_name,
                        {"plan": [first_week, second_week],
                         "plan2": [first_week]})


@pytest.fixture
def behavioral_test_fixture():
    """
    Basic test fixture.
    """

    test = BehavioralTest()
    yield test
    test.teardown()


@pytest.fixture
def test_with_workout_tables():
    """
    Test with workout tables.
    """

    test = BehavioralTest()
    test.workout_tables = []

    table1 = create_workout_table("table_id_1", "table_name_1")
    test.data_model.workout_plans.update_workout_table(table1)
    test.workout_tables.append(table1)

    table2 = WorkoutTable("table_id_2", "table_name_2", {"plan": []})
    test.data_model.workout_plans.update_workout_table(table2)
    test.workout_tables.append(table2)

    yield test
    test.teardown()


@pytest.fixture
def test_with_user_with_workouts():
    """
    Test suite with authorized user with workouts in TRAINING state.
    """

    test = BehavioralTest()
    test.workout_tables = []

    table = create_workout_table()
    test.data_model.workout_plans.update_workout_table(table)
    test.workout_tables.append(table)

    user = test.add_authorized_user()
    user.set_table(table.table_id)
    plan = test.get_table_plan(table, 0)
    user.set_page(plan)
    user.set_user_action(UserAction.TRAINING)

    yield test
    test.teardown()
