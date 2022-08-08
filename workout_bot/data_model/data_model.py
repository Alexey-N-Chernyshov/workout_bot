"""
Provides business data model objects.
"""

from .statistics import Statistics
from .users import Users
from .workout_plans import WorkoutPlans
from .workout_table_names import WorkoutTableNames


class DataModel:
    """
    An interface to all business data model objects.
    """

    statistics = Statistics()
    # {name: link}
    excercise_links = {}
    # Workouts has been read from tables
    workout_plans = WorkoutPlans()

    def __init__(self, feeder, users_storage_filename, table_ids_filename):
        self.feeder = feeder
        self.users = Users(users_storage_filename)
        self.workout_table_names = WorkoutTableNames(table_ids_filename)

    def update_tables(self):
        """
        Loads latest workout plans from google spreadsheets.
        """

        self.feeder.load_workouts(self.workout_plans,
                                  self.workout_table_names)
        self.statistics.set_training_plan_update_time()
