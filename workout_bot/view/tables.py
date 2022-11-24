"""
Representation of a table ids and pages
"""

from .utils import escape_text


def get_table_message(data_model, table_id):
    """
    Returns representation of a table with all pages.
    """

    text = ""
    if data_model.workout_table_names.is_table_present(table_id):
        spreadsheet_id = escape_text(table_id)
        table_name = data_model.workout_plans.get_plan_name(table_id)
        if not table_name:
            table_name = "Без названия"
        text += "*" + f"[{table_name}]"
        text += f"(https://docs.google.com/spreadsheets/d/{spreadsheet_id})*\n"
        text += "id: " + spreadsheet_id + "\n"
        text += "Страницы:\n"
        pages = data_model.workout_table_names.get_tables()[table_id]
        for page in pages:
            text += escape_text(" - " + page) + "\n"
    return text


def get_all_tables_message(data_model):
    """
    Returns only table names as a list.
    """

    text = ""
    for table_id in data_model.workout_table_names.get_tables():
        text += get_table_message(data_model, table_id)

    if not text:
        text = "Нет таблиц"

    return text
