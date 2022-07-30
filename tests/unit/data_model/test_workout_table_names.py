from workout_bot.data_model.workout_table_names import WorkoutTableNames
import os

def delete_file(filename):
    try:
        os.remove(filename)
    except OSError:
        pass


def test_persistence_when_new_item_added():
    STORAGE = "storage"
    delete_file(STORAGE)

    tables = WorkoutTableNames()
    tables.set_storage(STORAGE)

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
    tables_loaded = WorkoutTableNames()
    tables_loaded.set_storage(STORAGE)

    stored_tables = tables_loaded.get_tables()
    assert len(stored_tables["tablename"]) == 3
    assert "page1" in stored_tables["tablename"]
    assert "page2" in stored_tables["tablename"]
    assert "page3" in stored_tables["tablename"]

    delete_file(STORAGE)


def test_persistence_when_item_deleted():
    STORAGE = "storage"
    delete_file(STORAGE)

    tables = WorkoutTableNames()
    tables.set_storage(STORAGE)

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
    tables_loaded = WorkoutTableNames()
    tables_loaded.set_storage(STORAGE)

    stored_tables = tables_loaded.get_tables()
    assert len(stored_tables["tablename"]) == 1
    assert "page1" in stored_tables["tablename"]

    delete_file(STORAGE)
