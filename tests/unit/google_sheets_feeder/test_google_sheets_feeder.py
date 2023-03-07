"""
Tests for GoogleSheetsFeeder.
"""


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

    def parse_exercise_links(self, values):
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
