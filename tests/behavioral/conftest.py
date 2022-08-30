"""
Fixtures for behavioral tests.
"""

import datetime
import pytest
from workout_bot.data_model.workout_plans import WeekRoutine, WorkoutTable
from .behavioral_test_fixture import BehavioralTest


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

    first_week = WeekRoutine(datetime.date(2022, 8, 29),
                             datetime.date(2022, 9, 4),
                             1,
                             [],
                             "")
    table1 = WorkoutTable("table_id_1", "table_name_1", {"plan": [first_week]})
    test.data_model.workout_plans.update_workout_table(table1)
    test.workout_tables.append(table1)

    table2 = WorkoutTable("table_2", "table_name_2", {"plan": []})
    test.data_model.workout_plans.update_workout_table(table2)
    test.workout_tables.append(table2)

    yield test
    test.teardown()
