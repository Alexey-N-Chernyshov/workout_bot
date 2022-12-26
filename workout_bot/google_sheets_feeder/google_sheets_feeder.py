"""
The feeder provides data from google sheets.
"""

import logging
from data_model.workout_plans import WorkoutTable, WorkoutPlans


class GoogleSheetsFeeder:
    """
    Loads and transforms data from Google Spreadsheets.
    """

    def __init__(self, loader, adapter):
        self.loader = loader
        self.adapter = adapter

    def get_exercise_links(self, table_id, page_name):
        """
        Loads exercise links.
        """

        values = self.loader.get_values(table_id, page_name)
        return self.adapter.parse_exercise_links(values)

    def get_workout_table(self, table_id, page_names):
        """
        Parses a single workout table from Google Spreadsheet document.
        """

        table = WorkoutTable(table_id, "", {})
        for page_name in page_names:
            text = (
                "Loading "
                "https://docs.google.com/spreadsheets/d/"
                f"{table_id}/edit#gid=0 - \"{page_name}\""
            )
            logging.info(text)
            (table_name, merges, values) = self.loader \
                .get_values_and_merges(table_id, page_name)
            table.table_name = table_name
            logging.info("Parsing %s - %s", table_name, page_name)
            all_weeks = self.adapter.parse_table_page(merges, values)
            table.pages[page_name] = all_weeks
            logging.info("Loaded %s - %s", table_name, page_name)
        return table

    def get_workouts(self, workout_tables):
        """
        Loads workouts.
        """

        plans = WorkoutPlans()
        for table_id, page_names in workout_tables.get_tables().items():
            plans.update_workout_table(self.get_workout_table(table_id,
                                                              page_names))

        return plans
