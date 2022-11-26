"""
Tests for workout plans data model.
"""

from workout_bot.data_model.workout_plans import WorkoutPlans
from workout_bot.data_model.workout_plans import WorkoutTable


def test_workout_table_ids():
    """
    is_table_id_present returns True when table id is present and False
    otherwise.
    """

    table = WorkoutTable("table_id", "table_name", {})
    workout_plans = WorkoutPlans()
    workout_plans.update_workout_table(table)

    assert workout_plans.is_table_id_present("table_id")
    assert not workout_plans.is_table_id_present("not_present")
