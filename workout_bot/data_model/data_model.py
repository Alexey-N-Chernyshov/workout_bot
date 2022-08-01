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

    users = Users()
    statistics = Statistics()
    # {name: link}
    excercise_links = {}
    workout_table_names = WorkoutTableNames()
    # Workouts has been read from tables
    workout_plans = WorkoutPlans()

    def __init__(self, feeder):
        self.feeder = feeder

    def update_tables(self):
        """
        Loads latest workout plans from google spreadsheets.
        """

        self.feeder.load_workouts(self.workout_plans,
                                  self.workout_table_names)
        self.statistics.set_training_plan_update_time()
