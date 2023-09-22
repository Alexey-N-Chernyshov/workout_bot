"""
Tests for DataModel.
"""

from mock import Mock
from workout_bot.data_model.data_model import DataModel, PageReference
from workout_bot.notification import Notification


USER_STORAGE = "user_storage"
EXERCISES_TABLE_ID = "exercise_table_id"
EXERCISES_PAGE_NAME = "exercise_page_name"
TABLES_STORAGE = "table_storage"


def test_update_exercise_load_error(tmp_path):
    """
    Given: No errors and loader throws HttpError when updates exercises.
    When: update_tables() called.
    Then: HttpError is saved to data_model.notifications and
    workout_plans.update() was called.
    """

    user_storage_path = str(tmp_path / USER_STORAGE)
    table_storage_path = str(tmp_path / TABLES_STORAGE)

    error_title = "error title"
    error_detail = "detailed descr"
    data_model = DataModel(
        user_storage_path,
        table_storage_path,
        PageReference(EXERCISES_TABLE_ID, EXERCISES_PAGE_NAME)
    )
    data_model.exercise_links.update_exercise_links = Mock(
        name="update_exercise_links",
        side_effect=Notification(error_title, error_detail)
    )
    data_model.workout_plans.update = Mock(
        name="workout_plans.update"
    )

    data_model.update_tables()

    assert len(data_model.notifications.list()) == 1
    error = data_model.notifications.get_last()
    assert error.title == error_title
    assert error.description == error_detail
    data_model.workout_plans.update.assert_called_with(
        data_model.feeder,
        data_model.workout_table_names
    )


def test_update_workouts_load_error(tmp_path):
    """
    Given: No errors and loader throws HttpError when updates workouts.
    When: get_workouts() called.
    Then: HttpError is saved to data_model.notifications.
    """

    user_storage_path = str(tmp_path / USER_STORAGE)
    table_storage_path = str(tmp_path / TABLES_STORAGE)

    error_title = "error title"
    error_detail = "detailed descr"
    data_model = DataModel(
        user_storage_path,
        table_storage_path,
        PageReference(EXERCISES_TABLE_ID, EXERCISES_PAGE_NAME)
    )
    # successful call
    data_model.exercise_links.update_exercise_links = Mock(
        name="update_exercise_links",
    )
    data_model.workout_plans.update = Mock(
        name="update_exercise_links",
        side_effect=Notification(error_title, error_detail)
    )

    data_model.update_tables()

    assert len(data_model.notifications.list()) == 1
    error = data_model.notifications.get_last()
    assert error.title == error_title
    assert error.description == error_detail
