"""
Tests for DataModel.
"""

from mock import Mock
from workout_bot.data_model.data_model import DataModel, PageReference
from workout_bot.error import Error
from .utils import delete_file


USER_STORAGE = "user_storage"
EXERCISES_TABLE_ID = "exercise_table_id"
EXERCISES_PAGE_NAME = "exercise_page_name"
TABLES_STORAGE = "table_storage"


def test_update_exercise_load_error():
    """
    Given: No errors and loader throws HttpError when updates exercises.
    When: update_tables() called.
    Then: HttpError is saved to data_model.errors.
    """

    delete_file(USER_STORAGE)
    delete_file(TABLES_STORAGE)

    error_title = "error title"
    error_detail = "detailed descr"
    data_model = DataModel(
        USER_STORAGE,
        PageReference(EXERCISES_TABLE_ID, EXERCISES_PAGE_NAME),
        TABLES_STORAGE,
    )
    data_model.exercise_links.update_exercise_links = Mock(
        name="update_exercise_links",
        side_effect=Error(error_title, error_detail)
    )

    data_model.update_tables()

    assert len(data_model.errors.list()) == 1
    error = data_model.errors.get_last()
    assert error.title == error_title
    assert error.description == error_detail


def test_update_workouts_load_error():
    """
    Given: No errors and loader throws HttpError when updates workouts.
    When: get_workouts() called.
    Then: HttpError is saved to data_model.errors.
    """

    delete_file(USER_STORAGE)
    delete_file(TABLES_STORAGE)

    error_title = "error title"
    error_detail = "detailed descr"
    data_model = DataModel(
        USER_STORAGE,
        PageReference(EXERCISES_TABLE_ID, EXERCISES_PAGE_NAME),
        TABLES_STORAGE,
    )
    data_model.exercise_links.update_exercise_links = Mock(
        name="update_exercise_links",
    )
    data_model.feeder.get_workouts = Mock(
        name="update_exercise_links",
        side_effect=Error(error_title, error_detail)
    )

    data_model.update_tables()

    assert len(data_model.errors.list()) == 1
    error = data_model.errors.get_last()
    assert error.title == error_title
    assert error.description == error_detail
