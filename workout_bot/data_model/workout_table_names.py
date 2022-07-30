import shelve


class WorkoutTableNames:
    """
    Stores google table ids and pages with workouts to be loaded.
    """

    __storage_filename = ""

    # Table ids and page names to read
    # {google_spreadsheet_id: [page names]}
    workout_table_names = {}

    def set_storage(self, filename):
        self.__storage_filename = filename
        self.workout_table_names = shelve.open(self.__storage_filename,
                                               writeback=True)

    def is_table_present(self, table_id):
        return table_id in self.workout_table_names

    def add_table(self, table_id, pages):
        if pages:
            if table_id in self.workout_table_names:
                self.workout_table_names[table_id].update(pages)
                self.workout_table_names.sync()
            else:
                self.workout_table_names[table_id] = set(pages)
                self.workout_table_names.sync()

    def remove_table(self, table_id, pages):
        if table_id in self.workout_table_names:
            for page in pages:
                self.workout_table_names[table_id].remove(page)
                self.workout_table_names.sync()
            if not self.workout_table_names[table_id]:
                self.workout_table_names.pop(table_id, None)
                self.workout_table_names.sync()

    def get_tables(self):
        return self.workout_table_names
