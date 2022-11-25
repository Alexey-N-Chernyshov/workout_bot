"""
Test table representations.
"""

from workout_bot.view.tables import get_all_tables_message


class MockDataModel:
    class MockWorkoutTableNames:
        def __init__(self):
            self.tables = {}

        def is_table_present(self, table_id):
            return table_id in self.tables

        def get_tables(self):
            return self.tables

    class MockWorkoutPlans:
        def __init__(self):
            self.table_names = {}

        def get_plan_name(self, table_id):
            return self.table_names.get(table_id, None)

    def __init__(self):
        self.workout_table_names = self.MockWorkoutTableNames()
        self.workout_plans = self.MockWorkoutPlans()


def test_no_tables():
    """
    Tests none tables representation.
    """

    data_model = MockDataModel()

    expected = "Нет таблиц"

    assert expected == get_all_tables_message(data_model)


def test_named_tables_view():
    """
    Tests table representation.
    """

    table_id = "id"
    table_name = "table name"
    pages = ["page"]
    data_model = MockDataModel()
    data_model.workout_table_names.tables[table_id] = pages
    data_model.workout_plans.table_names[table_id] = table_name

    expected = f"*[{table_name}]"
    expected += f"(https://docs.google.com/spreadsheets/d/{table_id})*\n"
    expected += f"id: {table_id}\n"
    expected += "Страницы:\n"
    for page in pages:
        expected += f" \\- {page}\n"
    expected += "\n"

    assert expected == get_all_tables_message(data_model)


def test_unnamed_tables_view():
    """
    Tests table representation without name.
    """

    table_id = "id"
    pages = ["page"]
    data_model = MockDataModel()
    data_model.workout_table_names.tables[table_id] = pages

    expected = "*[Без названия]"
    expected += f"(https://docs.google.com/spreadsheets/d/{table_id})*\n"
    expected += "id: id\n"
    expected += "Страницы:\n"
    expected += " \\- page\n"
    expected += "\n"

    assert expected == get_all_tables_message(data_model)
