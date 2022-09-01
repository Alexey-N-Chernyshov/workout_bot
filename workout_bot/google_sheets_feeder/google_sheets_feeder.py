"""
The feeder provides data from google sheets.
"""


class GoogleSheetsFeederLoadingException(Exception):
    """
    Error during loading happened.
    """

    def __init__(self, table_id, pagename):
        self.table_id = table_id
        self.pagename = pagename
        super().__init__(f"Error while loading {table_id} {pagename}")


class GoogleSheetsFeederParsingException(Exception):
    """
    Error during parsing happened.
    """

    def __init__(self, table_id, pagename):
        self.table_id = table_id
        self.pagename = pagename
        super().__init__(f"Error while parsing {table_id} {pagename}")


class GoogleSheetsFeeder:
    """
    Loads and transforms data from Google Spreadsheets.
    """

    def __init__(self, loader, adapter):
        self.loader = loader
        self.adapter = adapter

    def get_excercise_links(self, table_id, pagename):
        """
        Loads excercise links.
        """
        values = None
        try:
            values = self.loader.get_values(table_id, pagename)
        except Exception as exception:
            raise GoogleSheetsFeederLoadingException(table_id, pagename) \
                from exception

        try:
            return self.adapter.parse_excercise_links(values)
        except Exception as exception:
            raise GoogleSheetsFeederParsingException(table_id, pagename) \
                from exception

    def get_workouts(self, workout_plans, tables):
        """
        Loads workouts.
        """

        return self.adapter.parse_workouts(self.loader, workout_plans, tables)
