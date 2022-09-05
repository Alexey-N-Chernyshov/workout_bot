"""
Tests related to admin table management.
"""

from workout_bot.data_model.users import UserAction
from workout_bot.view.tables import get_all_tables_message


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
