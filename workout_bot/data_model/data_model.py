from data_model.statistics import Statistics
from data_model.users import Users
from data_model.workout_plan import WorkoutLibrary
from data_model.workout_table_names import WorkoutTableNames


class DataModel:
    users = Users()
    statistics = Statistics()
    workout_table_names = WorkoutTableNames()

    # Workouts has been read from tables
    workout_library = WorkoutLibrary()

    def __init__(self, feeder):
        self.feeder = feeder

    def update_tables(self):
        self.feeder.load_workouts(self.workout_library,
                                  self.workout_table_names)
        self.statistics.set_training_plan_update_time()
