"""
Tests related to admin table management.
"""

from workout_bot.data_model.users import UserAction
from workout_bot.view.tables import (
    get_all_tables_message, get_table_name_message
)
from workout_bot.view.utils import escape_text
from workout_bot.controllers.table_management import TableManagementController


async def test_go_table_management(test_table_management):
    """
    Given: Alice is admin and state is ADMINISTRATION
    When: Alice sends got to table administration
    Then: Alice is in ADMIN_TABLE_MANAGEMENT state and table administration
    panel shown.
    """

    alice = test_table_management.users[0]
    alice.set_user_action(UserAction.ADMINISTRATION)

    await alice.send_message("Управление таблицами")

    expected = "Управление таблицами"
    alice.expect_answer(expected)
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.ADMIN_TABLE_MANAGEMENT)


async def test_show_all_tables(test_table_management):
    """
    Given: Alice is an admin and in ADMIN_TABLE_MANAGEMENT and wants to display
    all tables and tables present.
    When: Alice sends show all tables.
    Then: All tables are shown.
    """

    alice = test_table_management.users[0]

    await alice.send_message("Показать все таблицы")

    expected = get_all_tables_message(test_table_management.data_model)
    alice.expect_answer(expected)
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.ADMIN_TABLE_MANAGEMENT)


async def test_table_management_admin_adds_table(test_table_management):
    """
    Given: Admin is in ADMIN_TABLE_MANAGEMENT state.
    When: Admin sends add table message.
    Then: Admin is asked to enter table link and admin state is
    ADMIN_ADDING_TABLE.
    """

    alice = test_table_management.users[0]
    alice.set_user_action(UserAction.ADMIN_TABLE_MANAGEMENT)

    await alice.send_message("Добавить таблицу")

    expected = "Введите ссылку на таблицу"
    alice.expect_answer(expected)
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.ADMIN_ADDING_TABLE)


async def test_table_management_admin_cancel_adds_table(test_table_management):
    """
    Given: Admin is in ADMIN_ADDING_TABLE state.
    When: Admin sends cancel message.
    Then: Admin state is ADMIN_TABLE_MANAGEMENT.
    """

    alice = test_table_management.users[0]
    alice.set_user_action(UserAction.ADMIN_ADDING_TABLE)

    await alice.send_message("Отмена")

    expected = "Управление таблицами"
    alice.expect_answer(expected)
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.ADMIN_TABLE_MANAGEMENT)


async def test_admin_adds_table_link(test_table_management):
    """
    Given: Admin is in ADMIN_ADDING_TABLE state.
    When: Admin sends valid link to table
    Then: Admin is asked to choose pages.
    """

    alice = test_table_management.users[0]
    alice.set_user_action(UserAction.ADMIN_ADDING_TABLE)
    table_id = "1x2DpoqS9lxUNNWKf5hp4VhHWblWZm-mTTu5I5L3jhtw"

    await alice.send_message("https://docs.google.com/spreadsheets/d/" +
                             table_id)

    expected = "Добавление таблицы\n"
    expected += get_table_name_message(table_id, table_id)
    expected += "id: " + escape_text(table_id) + "\n"
    expected += "\n"
    expected += "Отметьте страницы с тренировками\n"
    expected += "🚫 \\- имя страницы имеет пробел в начале или в конце,"
    expected += "не может быть добавлена\n"
    expected += "⏺ \\- страница не добавлена\n"
    expected += "✅ \\- страница добавлена"

    alice.expect_answer(expected)
    alice.expect_answer("Управление таблицами")
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.ADMIN_TABLE_MANAGEMENT)


async def test_admin_adds_table_invalid_link(test_table_management):
    """
    Given: Admin is in ADMIN_ADDING_TABLE state.
    When: Admin sends invalid link to table
    Then: Admin is shown error message
    """

    alice = test_table_management.users[0]
    alice.set_user_action(UserAction.ADMIN_ADDING_TABLE)

    await alice.send_message("invalid link")

    alice.expect_answer("Ошибка при загрузке таблицы")
    alice.expect_answer("Введите ссылку на таблицу")
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.ADMIN_ADDING_TABLE)


async def test_admin_changes_table(test_table_management):
    """
    Given: Admin is in ADMIN_TABLE_MANAGEMENT state.
    When: Admin sends change table message.
    Then: Select table to change is shown.
    """

    alice = test_table_management.users[0]
    alice.set_user_action(UserAction.ADMIN_TABLE_MANAGEMENT)

    await alice.send_message("Изменить таблицу")

    alice.expect_answer("Выберите таблицу для редактирования")
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.ADMIN_TABLE_MANAGEMENT)


async def test_update_tables(test_table_management):
    """
    Given: Alice is an admin and in ADMIN_TABLE_MANAGEMENT and wants to update
    tables and tables are present.
    When: Alice sends update tables.
    Then: All tables are updated.
    """

    alice = test_table_management.users[0]

    await alice.send_message("Прочитать таблицы")

    expected = "Идёт обновление таблиц, может занять несколько секунд"
    alice.expect_answer(expected)
    alice.expect_answer("Таблицы обновлены")
    alice.expect_answer("Управление таблицами")
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.ADMIN_TABLE_MANAGEMENT)
    assert test_table_management.data_model.updated


async def test_go_administration(test_table_management):
    """
    Given: Alice is an admin and in ADMIN_TABLE_MANAGEMENT.
    When: Alice sends go to administration.
    Then: Alice is in ADMINISTRATION.
    """

    alice = test_table_management.users[0]

    await alice.send_message("Администрирование")

    alice.expect_answer("Администрирование")
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.ADMINISTRATION)


async def test_unrecognized_text(test_table_management):
    """
    Given: Alice is an admin and in ADMIN_TABLE_MANAGEMENT.
    When: Alice sends message with inrecognized test.
    Then: Alice is in ADMIN_TABLE_MANAGEMENT.
    """

    alice = test_table_management.users[0]

    await alice.send_message("unrecognized")

    alice.expect_answer("Управление таблицами")
    alice.expect_no_more_answers()
    alice.assert_user_action(UserAction.ADMIN_TABLE_MANAGEMENT)


async def test_admin_adds_page(test_table_management):
    """
    Given: Admin in ADMIN_TABLE_MANAGEMENT state and inline keyboard shown.
    Page hasn't been added.
    When: Admin presses inline keyboard with page.
    Then: Page is added to the table.
    """

    alice = test_table_management.users[0]
    table = test_table_management.workout_tables[0]
    table_id = table.table_id
    assert len(table.pages) == 2
    pages = list(table.pages.keys())
    page0 = pages[0]
    page1 = pages[1]

    data = TableManagementController.InlineKeyboardData(
        TableManagementController.QUERY_ACTION_SWITCH_PAGE,
        "new page"
    ).encode()
    message_text = "Добавление таблицы\n"
    message_text += "New table\n"
    message_text += f"id: {table_id}\n"
    await alice.press_inline_button(message_text, data)

    updated_table = test_table_management.data_model.workout_table_names \
        .get_tables()[table_id]
    assert len(updated_table) == 3
    assert page0 in updated_table
    assert page1 in updated_table
    assert "new page" in updated_table
    alice.assert_user_action(UserAction.ADMIN_TABLE_MANAGEMENT)
    alice.expect_no_more_answers()


async def test_admin_adds_invalid_page(test_table_management):
    """
    Given: Admin in ADMIN_TABLE_MANAGEMENT state and inline keyboard shown.
    Page has trailing whitespace, page is invalid. Page hasn't been added.
    When: Admin presses inline keyboard with page.
    Then: Page is not added, invalid page message is shown.
    """

    alice = test_table_management.users[0]
    table = test_table_management.workout_tables[0]
    table_id = table.table_id
    assert len(table.pages) == 2
    pages = list(table.pages.keys())
    page0 = pages[0]
    page1 = pages[1]

    page_name = "invalid page with trailing whitespace "
    data = TableManagementController.InlineKeyboardData(
        TableManagementController.QUERY_ACTION_SWITCH_PAGE,
        page_name
    ).encode()
    message_text = "Добавление таблицы\n"
    message_text += "New table\n"
    message_text += f"id: {table_id}\n"
    await alice.press_inline_button(message_text, data)

    updated_table = test_table_management.data_model.workout_table_names \
        .get_tables()[table_id]
    assert len(updated_table) == 2
    assert page0 in updated_table
    assert page1 in updated_table
    alice.assert_user_action(UserAction.ADMIN_TABLE_MANAGEMENT)
    expected = f"Имя страницы '{page_name}' имеет пробел в начале или в "
    expected += "конце, страница не может быть добавлена"
    alice.expect_answer(expected)
    alice.expect_no_more_answers()


async def test_admin_removes_page(test_table_management):
    """
    Given: Admin in ADMIN_TABLE_MANAGEMENT state and inline keyboard shown.
    Page has been added.
    When: Admin presses inline keyboard with page.
    Then: Page is deleted from the table.
    """

    alice = test_table_management.users[0]
    table = test_table_management.workout_tables[0]
    table_id = table.table_id
    assert len(table.pages) == 2
    pages = list(table.pages.keys())
    page_to_delete = pages[0]
    page1 = pages[1]

    data = TableManagementController.InlineKeyboardData(
        TableManagementController.QUERY_ACTION_SWITCH_PAGE,
        page_to_delete
    ).encode()
    message_text = "Добавление таблицы\n"
    message_text += "New table\n"
    message_text += f"id: {table_id}\n"
    await alice.press_inline_button(message_text, data)

    updated_table = test_table_management.data_model.workout_table_names \
        .get_tables()[table_id]
    assert len(updated_table) == 1
    assert page1 in updated_table
    alice.assert_user_action(UserAction.ADMIN_TABLE_MANAGEMENT)
    alice.expect_no_more_answers()


async def test_admin_chooses_table_to_change(test_table_management):
    """
    Given: Admin is in ADMIN_TABLE_MANAGEMENT state and inline keyboard shown.
    When: Admin presses inline keyboard with table to change chosen.
    Then: Changing table message is shown .
    """

    alice = test_table_management.users[0]
    table_id = test_table_management.workout_tables[1].table_id
    table_name = test_table_management.workout_tables[1].table_name

    data = TableManagementController.InlineKeyboardData(
        TableManagementController.QUERY_ACTION_CHOOSE_TABLE,
        table_id
    ).encode()
    message_text = "Выберите таблицу для редактирования"
    await alice.press_inline_button(message_text, data)

    expected = "Редактирование таблицы\n"
    expected += get_table_name_message(table_name, table_id)
    expected += "id: " + escape_text(table_id) + "\n"
    expected += "\n"
    expected += "Отметьте страницы с тренировками\n"
    expected += "🚫 \\- имя страницы имеет пробел в начале или в конце,"
    expected += "не может быть добавлена\n"
    expected += "⏺ \\- страница не добавлена\n"
    expected += "✅ \\- страница добавлена"

    alice.expect_answer(expected)
    alice.assert_user_action(UserAction.ADMIN_TABLE_MANAGEMENT)
    alice.expect_no_more_answers()
