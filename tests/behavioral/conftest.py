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

    workout1 = Workout(table_name + "workout1", [], 1, 1)
    workout2 = Workout(table_name + "workout2", [], 1, 1)
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
                        {table_name + "plan": [first_week, second_week],
                         table_name + "plan2": [first_week]})


@pytest.fixture(name="behavioral_test_fixture")
def fixture_behavioral(tmp_path):
    """
    Basic test fixture.
    """

    test = BehavioralTest(tmp_path)
    yield test


@pytest.fixture(name="test_with_workout_tables")
def fixture_with_workout_tables(tmp_path):
    """
    Test with workout tables.
    """

    test = BehavioralTest(tmp_path)
    test.workout_tables = []

    test.table1 = create_workout_table("table_id_1", "table_name_1")
    test.add_table(test.table1)

    test.table2 = create_workout_table("table_id_2", "table_name_2")
    test.add_table(test.table2)

    yield test


@pytest.fixture(name="test_alice_training")
def fixture_alice_training(test_with_workout_tables):
    """
    Alice is a user, and she is TRAINING, and table and plan is set.
    """

    test = test_with_workout_tables
    test.alice = test.add_user_context()
    test.alice.set_table(test.table1.table_id)
    test.plan = list(test.table1.pages)[0]
    test.alice.set_page(test.plan)
    test.alice.set_user_action(UserAction.TRAINING)

    yield test


@pytest.fixture(name="test_with_user_with_workouts")
def fixture_with_user_with_workouts(tmp_path):
    """
    Test suite with authorized user with workouts in TRAINING state.
    """

    test = BehavioralTest(tmp_path)
    test.workout_tables = []

    test.table = create_workout_table("table_id_1", "table_name_1")
    test.add_table(test.table)

    user = test.add_user_context()
    user.set_table(test.table.table_id)
    plan = list(test.table.pages)[0]
    user.set_page(plan)
    user.set_user_action(UserAction.TRAINING)

    yield test


@pytest.fixture(name="test_table_management")
def fixture_table_management(test_with_workout_tables):
    """
    Sets up tables and admin in ADMIN_TABLE_MANAGEMENT state.
    """

    test = test_with_workout_tables
    admin = test.add_admin()
    admin.set_user_action(UserAction.ADMIN_TABLE_MANAGEMENT)
    yield test


@pytest.fixture(name="test_user_management")
# pylint: disable=redefined-outer-name
def fixture_user_management(tmp_path):
    """
    Sets up test data for user management tests.
    Users:
     - admin
     - user
     - blocked
    """

    test = BehavioralTest(tmp_path)
    test.workout_table = create_workout_table("Table_id_1", "Table_name_1")
    test.add_table(test.workout_table)
    test.table_id = test.workout_table.table_id
    test.table_name = test.workout_table.table_name

    test.admin = test.add_admin(user_name="admin")
    test.admin.set_user_action(UserAction.ADMIN_USER_MANAGEMENT)
    test.admin.set_table(test.table_id)

    test.waiting = test.add_user_context(
        user_name="waiting",
        action=UserAction.AWAITING_AUTHORIZATION
    )

    test.user = test.add_user_context(user_name="user")
    test.user.set_user_action(UserAction.TRAINING)
    test.user.set_table(test.table_id)

    test.blocked = test.add_user_context(user_name="blocked")
    test.blocked.set_user_action(UserAction.BLOCKED)

    yield test
