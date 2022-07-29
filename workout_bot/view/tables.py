from view.util import escape_text


def get_table_message(data_model, table_id):
    text = ""
    if data_model.is_table_present(table_id):
        table_name = data_model.workout_library.get_plan_name(table_id)
        if table_name:
            text += "*" + table_name + "*\n"
        text += "id: " + escape_text(table_id) + "\n"
        text += "Страницы:\n"
        pages = data_model.get_tables()[table_id]
        for page in pages:
            text += escape_text(" - " + page) + "\n"
    return text


def get_all_tables_message(data_model):
    text = ""
    for table_id, pages in data_model.get_tables().items():
        text += get_table_message(data_model, table_id)
        text += "\n"
    return text
