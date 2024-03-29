"""
Provides business data model objects.
"""

from google_sheets_feeder.google_sheets_adapter import GoogleSheetsAdapter
from google_sheets_feeder.google_sheets_feeder import GoogleSheetsFeeder
from google_sheets_feeder.google_sheets_loader import GoogleSheetsLoader
from .exercise_links import ExerciseLinks
from .statistics import Statistics
from .users import Users
from .workout_plans import WorkoutPlans
from .workout_table_names import WorkoutTableNames


class DataModel:
    """
    An interface to all business data model objects.
    """

    def __init__(self,
                 users_storage_filename,
                 exercise_links_table_id,
                 exercise_links_pagename,
                 table_ids_filename):
        self.feeder = GoogleSheetsFeeder(GoogleSheetsLoader(),
                                         GoogleSheetsAdapter())
        self.users = Users(users_storage_filename)
        self.exercise_links = ExerciseLinks(exercise_links_table_id,
                                            exercise_links_pagename,
                                            self.feeder)
        self.workout_table_names = WorkoutTableNames(table_ids_filename)
        self.statistics = Statistics()
        # Workouts has been read from tables
        self.workout_plans = WorkoutPlans()

    def update_tables(self):
        """
        Loads the latest workout plans from Google spreadsheets.
        """

        self.exercise_links.load_exercise_links()
        self.workout_plans = self.feeder.get_workouts(self.workout_table_names)
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
