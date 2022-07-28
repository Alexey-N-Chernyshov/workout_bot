from data_model.statistics import Statistics
from data_model.users import Users
from data_model.workout_plan import WorkoutLibrary


class DataModel:
    workout_library = WorkoutLibrary()
    users = Users()
    statistics = Statistics()
    # {google spreadsheet_id: [page names]}
    workout_tables = {}

    def __init__(self, feeder):
        self.feeder = feeder

    def is_table_present(self, table_id):
        return table_id in self.workout_tables

    def update_tables(self):
        self.feeder.load_workouts(self.workout_library, self.workout_tables)
        self.statistics.set_training_plan_update_time()

    def add_table(self, table_id, pages):
        if pages:
            if table_id in self.workout_tables:
                for page in pages:
                    if not page in self.workout_tables[table_id]:
                        self.workout_tables[table_id].append(page)
            else:
                self.workout_tables[table_id] = pages

    def remove_table(self, table_id, pages):
        if table_id in self.workout_tables:
            for page in pages:
                self.workout_tables[table_id].remove(page)
            if not self.workout_tables[table_id]:
                self.workout_tables.pop(table_id, None)

    def get_tables(self):
        return self.workout_tables
