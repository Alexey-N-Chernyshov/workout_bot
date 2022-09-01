"""
The feeder provides data from google sheets.
"""


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

        return self.adapter \
            .parse_excercise_links(self.loader.get_values(table_id, pagename))

    def get_workouts(self, workout_plans, tables):
        """
        Loads workouts.
        """

        return self.adapter.parse_workouts(self.loader, workout_plans, tables)
