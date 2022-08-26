from workout_bot.data_model.workout_table_names import WorkoutTableNames
from .utils import delete_file


def test_persistence_when_new_item_added():
    STORAGE = "storage"
    delete_file(STORAGE)

    tables = WorkoutTableNames(STORAGE)

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
    tables_loaded = WorkoutTableNames(STORAGE)

    stored_tables = tables_loaded.get_tables()
    assert len(stored_tables["tablename"]) == 3
    assert "page1" in stored_tables["tablename"]
    assert "page2" in stored_tables["tablename"]
    assert "page3" in stored_tables["tablename"]

    delete_file(STORAGE)


def test_persistence_when_item_deleted():
    STORAGE = "storage"
    delete_file(STORAGE)

    tables = WorkoutTableNames(STORAGE)

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
    tables_loaded = WorkoutTableNames(STORAGE)

    stored_tables = tables_loaded.get_tables()
    assert len(stored_tables["tablename"]) == 1
    assert "page1" in stored_tables["tablename"]

    delete_file(STORAGE)


def test_table_deleted_when_all_pages_deleted():
    STORAGE = "storage"
    delete_file(STORAGE)

    tables = WorkoutTableNames(STORAGE)

    tables.add_table("tablename", ["page1"])
    stored_tables = tables.get_tables()

    tables.remove_table("tablename", ["page1"])
    stored_tables = tables.get_tables()

    assert "tablename" not in stored_tables

    delete_file(STORAGE)
