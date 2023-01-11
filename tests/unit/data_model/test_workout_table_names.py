"""
Tests for workout talbe names data model.
"""

from workout_bot.data_model.workout_table_names import WorkoutTableNames


STORAGE = "storage"


def test_persistence_when_new_item_added(tmp_path):
    """
    Test persistence storage allows to add items.
    """

    storage_path = str(tmp_path / STORAGE)
    tables = WorkoutTableNames(storage_path)

    tables.add_table("tablename", ["page1", "page2"])
    stored_tables = tables.get_tables()

    assert "tablename" in stored_tables
    assert len(stored_tables["tablename"]) == 2
    assert "page1" in stored_tables["tablename"]
    assert "page2" in stored_tables["tablename"]

    tables.add_table("tablename", ["page3"])
    stored_tables = tables.get_tables()

    assert len(stored_tables["tablename"]) == 3
    assert "page3" in stored_tables["tablename"]

    # close and reopen storage
    del stored_tables
    del tables
    tables_loaded = WorkoutTableNames(storage_path)

    stored_tables = tables_loaded.get_tables()
    assert len(stored_tables["tablename"]) == 3
    assert "page1" in stored_tables["tablename"]
    assert "page2" in stored_tables["tablename"]
    assert "page3" in stored_tables["tablename"]


def test_persistence_when_item_deleted(tmp_path):
    """
    Test persistence storage allows remove items.
    """

    storage_path = str(tmp_path / STORAGE)
    tables = WorkoutTableNames(storage_path)

    tables.add_table("tablename", ["page1", "page2"])
    stored_tables = tables.get_tables()

    assert "tablename" in stored_tables
    assert len(stored_tables["tablename"]) == 2
    assert "page1" in stored_tables["tablename"]
    assert "page2" in stored_tables["tablename"]

    tables.remove_table("tablename", ["page2"])
    stored_tables = tables.get_tables()

    assert len(stored_tables["tablename"]) == 1
    assert "page1" in stored_tables["tablename"]

    # close and reopen storage
    del stored_tables
    del tables
    tables_loaded = WorkoutTableNames(storage_path)

    stored_tables = tables_loaded.get_tables()
    assert len(stored_tables["tablename"]) == 1
    assert "page1" in stored_tables["tablename"]


def test_table_deleted_when_all_pages_deleted(tmp_path):
    """
    Test that table is deleted when there is no more pages left.
    """

    storage_path = str(tmp_path / STORAGE)
    tables = WorkoutTableNames(storage_path)

    tables.add_table("tablename", ["page1"])

    tables.remove_table("tablename", ["page1"])
    stored_tables = tables.get_tables()

    assert "tablename" not in stored_tables


def test_workout_plans_not_found(tmp_path):
    """
    Returns empty list when there is no table with table id.
    """

    storage_path = str(tmp_path / STORAGE)
    workout_plans = WorkoutTableNames(storage_path)

    plans = workout_plans.get_plan_names("not_present")

    assert not plans


def test_workout_plans_found(tmp_path):
    """
    Returns plans for table with table id if present.
    """

    storage_path = str(tmp_path / STORAGE)
    tables = WorkoutTableNames(storage_path)
    tables.add_table("table_id", ["page1", "page2"])

    plans = tables.get_plan_names("table_id")

    assert len(plans) == 2
    assert "page1" in plans
    assert "page2" in plans


def test_switch_page(tmp_path):
    """
    Page not present, inserts.
    Then, when page is present, removes it.
    """

    storage_path = str(tmp_path / STORAGE)
    tables = WorkoutTableNames(storage_path)
    tables.add_table("table_id", ["page1", "page2"])

    # add new page
    tables.switch_pages("table_id", "new page")
    plans = tables.get_plan_names("table_id")
    assert len(plans) == 3
    assert "page1" in plans
    assert "page2" in plans
    assert "new page" in plans

    # and remove new page
    tables.switch_pages("table_id", "new page")
    plans = tables.get_plan_names("table_id")
    assert len(plans) == 2
    assert "page1" in plans
    assert "page2" in plans


def test_switch_page_new_table(tmp_path):
    """
    Table not exists, inserts.
    """

    storage_path = str(tmp_path / STORAGE)
    tables = WorkoutTableNames(storage_path)

    # add new page
    tables.switch_pages("table_id", "new page")
    plans = tables.get_plan_names("table_id")
    assert len(plans) == 1
    assert "new page" in plans
