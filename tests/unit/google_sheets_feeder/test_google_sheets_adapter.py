"""
Tests for GoogleSheetsAdapter
"""

import pickle
import os
import pytest
from workout_bot.google_sheets_feeder.google_sheets_adapter \
    import GoogleSheetsAdapter
from .data.workouts_data import raw_table_data, expected_workouts


FIXTURE_DIR = os.path.dirname(os.path.realpath(__file__))


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
                for actual_excercise, expected_excercise in zip(
                        actual_sets.excersises, expected_sets.excersises):
                    assert actual_excercise.description == expected_excercise \
                        .description
                    assert actual_excercise.reps_window == expected_excercise \
                        .reps_window


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "data/excercises_raw.pkl"),
    os.path.join(FIXTURE_DIR, "data/excercises_expected.pkl"),
    )
def test_parse_workout_links(datafiles):
    """
    Loads excercises.pkl as it were from google table and transforms to the
    list of excercises. Expected ordered list of excercises stored at
    "data/excercises_expected.pkl"
    """

    adapter = GoogleSheetsAdapter()

    with open(datafiles.listdir()[0], "rb") as raw_file:
        with open(datafiles.listdir()[1], "rb") as expected_file:
            values = pickle.load(raw_file)
            actual = adapter.parse_excercise_links(values)
            expected = pickle.load(expected_file)

            for acutal_item, expected_item in zip(actual, expected):
                assert acutal_item == expected_item


def test_parse_workouts():
    """
    Raw table data is parsed into list of WeekRoutine.
    """

    adapter = GoogleSheetsAdapter()

    (_, merges, values) = raw_table_data

    parsed = adapter.parse_table_page(merges, values)

    assert_workouts_equal(parsed, expected_workouts)
