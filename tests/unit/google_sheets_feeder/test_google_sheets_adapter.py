"""
Tests for GoogleSheetsAdapter
"""

import pickle
import os
import pytest
from workout_bot.google_sheets_feeder.google_sheets_adapter \
    import GoogleSheetsAdapter


FIXTURE_DIR = os.path.dirname(os.path.realpath(__file__))


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "data/excercises_raw.pkl"),
    os.path.join(FIXTURE_DIR, "data/excercises_expected.pkl"),
    )
def test_workout_links(datafiles):
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
