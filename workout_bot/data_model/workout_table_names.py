from data_model.statistics import Statistics

class WorkoutTableNames:
    """
    Stores google table ids and pages with workouts to be loaded.
    """

    # Table ids and page names to read
    # {google_spreadsheet_id: [page names]}
    workout_table_names = {}

    def is_table_present(self, table_id):
        return table_id in self.workout_table_names

    def add_table(self, table_id, pages):
        if pages:
            if table_id in self.workout_table_names:
                for page in pages:
                    if page not in self.workout_table_names[table_id]:
                        self.workout_table_names[table_id].append(page)
            else:
                self.workout_table_names[table_id] = pages

    def remove_table(self, table_id, pages):
        if table_id in self.workout_table_names:
            for page in pages:
                self.workout_table_names[table_id].remove(page)
            if not self.workout_table_names[table_id]:
                self.workout_table_names.pop(table_id, None)

    def get_tables(self):
        return self.workout_table_names
