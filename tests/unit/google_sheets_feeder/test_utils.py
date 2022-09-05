"""
Tests for google_sheets_feeder utils.
"""

from workout_bot.google_sheets_feeder.utils import get_table_id_from_link


def test_get_table_id_from_link_example():
    "Tests that table id is correctly extracted from example link"

    link = "https://docs.google.com/spreadsheets/d/spreadsheetId/edit#gid=0"
    table_id = get_table_id_from_link(link)

    expected = "spreadsheetId"
    assert expected == table_id


def test_get_table_id_from_link_actual():
    "Tests that table id is correctly extracted from actual link"

    link = (
        "https://docs.google.com/spreadsheets/d/"
        "1MGO6-8NAEJEMrDpx6y4ni_HVofQ5lCisaseLaRJAEBk/edit#gid=4142461"
    )
    table_id = get_table_id_from_link(link)

    expected = "1MGO6-8NAEJEMrDpx6y4ni_HVofQ5lCisaseLaRJAEBk"
    assert expected == table_id


def test_get_table_id_from_link_prefix_malformed():
    "Tests that table id is not extracted from malformed link"

    link = "this/is/wrong_prefix/spreadsheets/d/spreadsheetId/edit#gid=0"
    table_id = get_table_id_from_link(link)

    assert table_id is None


def test_get_table_id_from_link_suffix_malformed():
    "Tests that table id is not extracted from malformed link"

    link = "https://docs.google.com/spreadsheets/d/spreadsheetId"
    table_id = get_table_id_from_link(link)

    assert table_id is None
