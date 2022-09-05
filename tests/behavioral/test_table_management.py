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
