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
        table_name = data_model.workout_plans.get_plan_name(table_id)
        if table_name:
            text += "*" + table_name + "*\n"
        text += "id: " + escape_text(table_id) + "\n"
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
        text += "\n"

    if not text:
        text = "Нет таблиц"

    return text
