"""
Tests for DataModel.
"""

from mock import Mock
from workout_bot.google_sheets_feeder.google_sheets_adapter import (
    GoogleSheetsAdapter
)
from workout_bot.google_sheets_feeder.google_sheets_feeder import (
    GoogleSheetsFeeder
)
from workout_bot.google_sheets_feeder.google_sheets_loader import (
    GoogleSheetsLoader
)
from workout_bot.data_model.data_model import DataModel, PageReference
from workout_bot.error import Error


STORAGE = "user_storage"
EXERCISES_TABLE_ID = "exercise_table_id"
EXERCISES_PAGE_NAME = "exercise_page_name"
TABLES_STORAGE = "table_storage"


def test_update_exercise_load_error():
    """
    Given: No errors and loader throws HttpError when updates exercises.
    When: update_tables() called.
    Then: HttpError is saved to data_model.errors.
    """

    error_title = "error title"
    error_detail = "detailed descr"
    loader = GoogleSheetsLoader()
    loader.get_values = Mock(
        name="get_values",
        side_effect=Error(error_title, error_detail)
    )
    adapter = GoogleSheetsAdapter()
    feeder = GoogleSheetsFeeder(loader, adapter)
    data_model = DataModel(
        STORAGE,
        PageReference(EXERCISES_TABLE_ID, EXERCISES_PAGE_NAME),
        TABLES_STORAGE,
        feeder=feeder
    )

    data_model.update_tables()

    assert len(data_model.errors.list()) == 1
    error = data_model.errors.get_last()
    assert error.title == error_title
    assert error.description == error_detail
