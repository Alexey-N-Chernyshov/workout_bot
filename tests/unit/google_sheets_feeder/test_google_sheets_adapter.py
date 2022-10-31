"""
Tests for GoogleSheetsAdapter
"""

import os
from workout_bot.google_sheets_feeder.google_sheets_adapter \
    import GoogleSheetsAdapter
from .data.workouts_data import raw_table_data, expected_workouts
from .data.exercises_data import raw_exercises_data, expected_exercise_data


FIXTURE_DIR = os.path.dirname(os.path.realpath(__file__))
EXCERCISES_RAW_FILE = os.path.join(FIXTURE_DIR, "data/exercises_raw.pkl")
EXCERCISES_EXPECTED_FILE = os.path.join(FIXTURE_DIR,
                                        "data/exercises_expected.pkl")


def test_parse_workout_links():
    """
    Loads exercises.pkl as it were from google table and transforms to the
    list of exercises. Expected ordered list of exercises stored at
    "data/exercises_expected.pkl"
    """

    adapter = GoogleSheetsAdapter()

    actual = adapter.parse_exercise_links(raw_exercises_data)

    for acutal_item, expected_item in zip(actual, expected_exercise_data):
        assert acutal_item == expected_item


def assert_workouts_equal(actual, expected):
    """
    Asserts actual and expected workouts are equal.
    """

    for actual_week, expected_week in zip(actual, expected):
        assert actual_week.start_date == expected_week.start_date
        assert actual_week.end_date == expected_week.end_date
        assert actual_week.number == expected_week.number
        assert actual_week.comment == expected_week.comment
        for actual_workout, expected_workout in zip(actual_week.workouts,
                                                    expected_week.workouts):
            assert actual_workout.description == expected_workout.description
            assert actual_workout.actual_number == expected_workout \
                .actual_number
            assert actual_workout.number == expected_workout.number
            for actual_sets, expected_sets in zip(actual_workout.sets,
                                                  expected_workout.sets):
                assert actual_sets.description == expected_sets.description
                assert actual_sets.number == expected_sets.number
                assert actual_sets.rounds == expected_sets.rounds
                for actual_exercise, expected_exercise in zip(
                        actual_sets.exercises, expected_sets.exercises):
                    assert actual_exercise.description == expected_exercise \
                        .description
                    assert actual_exercise.reps_window == expected_exercise \
                        .reps_window


def test_parse_workouts():
    """
    Raw table data is parsed into list of WeekRoutine.
    """

    adapter = GoogleSheetsAdapter()

    (_, merges, values) = raw_table_data

    parsed = adapter.parse_table_page(merges, values)

    assert_workouts_equal(parsed, expected_workouts)
