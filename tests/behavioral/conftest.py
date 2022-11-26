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
    test.add_table(table1)

    table2 = create_workout_table("table_id_2", "table_name_2")
    test.add_table(table2)

    yield test
    test.teardown()


@pytest.fixture
def test_with_user_with_workouts():
    """
    Test suite with authorized user with workouts in TRAINING state.
    """

    test = BehavioralTest()
    test.workout_tables = []

    table1 = create_workout_table("table_id_1", "table_name_1")
    test.add_table(table1)

    user = test.add_authorized_user()
    user.set_table(table1.table_id)
    plan = test.get_table_plan(table1, 0)
    user.set_page(plan)
    user.set_user_action(UserAction.TRAINING)

    yield test
    test.teardown()


@pytest.fixture
# pylint: disable=redefined-outer-name
def test_table_management(test_with_workout_tables):
    """
    Sets up tables and admin in ADMIN_TABLE_MANAGEMENT state.
    """

    test = test_with_workout_tables
    admin = test.add_admin()
    admin.set_user_action(UserAction.ADMIN_TABLE_MANAGEMENT)
    yield test
    test.teardown()


@pytest.fixture
# pylint: disable=redefined-outer-name
def test_user_management(test_with_workout_tables):
    """
    Sets up test data for user management tests.
    Users:
     - admin
     - user
     - blocked
    """

    test = test_with_workout_tables

    test.table_id = test.workout_tables[0].table_id
    test.table_name = test.workout_tables[0].table_name

    test.admin = test.add_admin(user_name="admin")
    test.admin.set_user_action(UserAction.ADMIN_USER_MANAGEMENT)
    test.admin.set_table(test.table_id)

    test.waiting = test.add_admin(user_name="waiting")
    test.waiting.set_user_action(UserAction.AWAITING_AUTHORIZATION)

    test.user = test.add_authorized_user(user_name="user")
    test.user.set_user_action(UserAction.TRAINING)
    test.user.set_table(test.table_id)

    test.blocked = test.add_authorized_user(user_name="blocked")
    test.blocked.set_user_action(UserAction.BLOCKED)

    yield test
    test.teardown()
