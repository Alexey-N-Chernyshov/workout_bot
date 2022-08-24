"""
Provides business data model objects.
"""

from .excercise_links import ExcerciseLinks
from .statistics import Statistics
from .users import Users
from .workout_plans import WorkoutPlans
from .workout_table_names import WorkoutTableNames


class DataModel:
    """
    An interface to all business data model objects.
    """

    statistics = Statistics()
    # Workouts has been read from tables
    workout_plans = WorkoutPlans()

    def __init__(self,
            feeder,
            users_storage_filename,
            excercise_links_table_id,
            excercise_links_pagename,
            table_ids_filename):
        self.feeder = feeder
        self.users = Users(users_storage_filename)
        self.excercise_links = ExcerciseLinks(excercise_links_table_id,
                                              excercise_links_pagename,
                                              feeder)
        self.workout_table_names = WorkoutTableNames(table_ids_filename)

    def update_tables(self):
        """
        Loads latest workout plans from google spreadsheets.
        """

        self.excercise_links.load_excercise_links()
        self.feeder.load_workouts(self.workout_plans,
                                  self.workout_table_names)
        self.statistics.set_training_plan_update_time()

    def next_workout_for_user(self, user_id):
        """
        Shifts the current workout for user if there are more workouts, if
        there is no more workouts, does nothing.
        """

        user_context = self.users.get_user_context(user_id)
        if user_context.current_workout < self.workout_plans \
                .get_workout_number(user_context.current_table_id,
                                    user_context.current_page,
                                    user_context.current_week) - 1:
            user_context.current_workout += 1
        elif user_context.current_week < self.workout_plans \
                .get_week_number(user_context.current_table_id,
                                 user_context.current_page) - 1:
            user_context.current_week += 1
            user_context.current_workout = 0
        self.users.set_user_context(user_context)
