"""
Tests for GoogleSheetsFeeder.
"""

import pytest
from workout_bot.google_sheets_feeder.google_sheets_feeder import (
    GoogleSheetsFeeder,
    GoogleSheetsFeederLoadingException,
    GoogleSheetsFeederParsingException
)


class GoogleSheetsLoaderMock:
    """
    Mock of GoogleSheetsLoader
    """

    def __init__(self, callback):
        self.callback = callback

    def get_values(self, table_id, pagename):
        """
        Mock function, calls callback.
        """

        del table_id
        del pagename

        self.callback()

    def get_values_and_merges(self, table_id, pagename):
        """
        Mock function, calls callback.
        """

        del table_id
        del pagename

        self.callback()


class GoogleSheetsAdapterMock:
    """
    Mock of GoogleSheetsAdapter
    """

    def __init__(self, callback):
        self.callback = callback

    def parse_excercise_links(self, values):
        """
        Mock function, calls callback.
        """

        del values

        self.callback()

    def parse_workouts(self):
        """
        Mock function, calls callback.
        """



def success_callback():
    """
    Successfull invocation.
    """

    return None


def failure_callback():
    """
    Raise basic exception.
    """

    raise Exception("Basic exception")


def test_excercise_load_exception():
    """
    Catch excercise loading exception.
    """

    feeder = GoogleSheetsFeeder(GoogleSheetsLoaderMock(failure_callback),
                                GoogleSheetsAdapterMock(success_callback))

    table_id = "table_id"
    pagename = "pagename"
    with pytest.raises(GoogleSheetsFeederLoadingException) as exception_info:
        feeder.get_excercise_links(table_id, pagename)

    assert exception_info.type is GoogleSheetsFeederLoadingException
    assert exception_info.value.table_id == table_id
    assert exception_info.value.pagename == pagename


def test_excercise_parse_exception():
    """
    Catch excercise parsing exception.
    """

    feeder = GoogleSheetsFeeder(GoogleSheetsLoaderMock(success_callback),
                                GoogleSheetsAdapterMock(failure_callback))

    table_id = "table_id"
    pagename = "pagename"
    with pytest.raises(GoogleSheetsFeederParsingException) as exception_info:
        feeder.get_excercise_links(table_id, pagename)

    assert exception_info.type is GoogleSheetsFeederParsingException
    assert exception_info.value.table_id == table_id
    assert exception_info.value.pagename == pagename


def test_no_exceptions():
    """
    Sunny day test, no exceptions.
    """

    feeder = GoogleSheetsFeeder(GoogleSheetsLoaderMock(success_callback),
                                GoogleSheetsAdapterMock(success_callback))

    table_id = "table_id"
    pagename = "pagename"
    feeder.get_excercise_links(table_id, pagename)
