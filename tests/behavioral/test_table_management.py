"""
Tests related to admin table management.
"""

from workout_bot.data_model.users import UserAction
from workout_bot.view.tables import get_all_tables_message


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
