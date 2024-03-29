"""
Provides access to workouts and plans.
"""

import threading
from datetime import date
from dataclasses import dataclass
from typing import List
from typing import Dict


@dataclass
class Exercise:
    """
    It's a single exercise.
    """

    description: str
    reps_window: str = ''
    weight: str = ''


@dataclass
class Set:
    """
    Is a set of exercises.
    """

    description: str
    number: int
    exercises: List[Exercise]
    rounds: str = ""

    def empty(self):
        """
        Returns false if has non empty description or exercises.
        """

        return not self.description and not self.exercises


@dataclass
class Workout:
    """
    Single workout consists of exercises combined into sets.
    """

    description: str
    sets: List[Set]
    actual_number: int
    number: int = 0

    def empty(self):
        """
        Returns false if has non empty description or exercise set.
        """

        for workout_set in self.sets:
            if not workout_set.empty():
                return False
        return not self.description


@dataclass
class WeekRoutine:
    """
    Workouts for a single week.
    """

    start_date: date
    end_date: date
    number: int
    workouts: List[Workout]
    comment: str


@dataclass
class WorkoutTable:
    """
    One workout table can have several plans each on one page. Plan is a list
    of week routines.
    """

    table_id: str
    table_name: str
    pages: Dict[str, List[WeekRoutine]]


class WorkoutPlans:
    """
    Thread-safe workout plans storage
    """

    def __init__(self):
        # map {table_id -> WorkoutTable}
        self.__workout_tables = {}
        self.lock = threading.Lock()

    def update_workout_table(self, workout_table):
        """
        Loads tables.
        """

        with self.lock:
            self.__workout_tables[workout_table.table_id] = workout_table

    def is_table_id_present(self, table_id):
        """
        Checks if table id is present.
        """
        with self.lock:
            return table_id in self.__workout_tables

    def get_table_names(self):
        """
        Returns all table names.
        """

        with self.lock:
            result = set()
            for table in self.__workout_tables.values():
                result.add(table.table_name)
            return result

    def get_plan_name(self, table_id):
        """
        Returns table name for table_id.
        """

        name = table_id
        with self.lock:
            if table_id in self.__workout_tables:
                name = self.__workout_tables[table_id].table_name
            return name

    def get_table_id_by_name(self, name):
        """
        Returns table id by table name.
        """

        res = None
        with self.lock:
            for table_id, table in self.__workout_tables.items():
                if table.table_name == name:
                    res = table_id
            return res

    def get_week_routine(self, table_id, page_name, week_number):
        """
        Returns week routine by table_id, page_name, and week_number.
        """

        with self.lock:
            return self.__workout_tables[table_id] \
                .pages[page_name][week_number]

    def get_workout(self, table_id, page_name, week_number, workout_number):
        """
        Returns workout by table_id, page_name, week_number, and
        workout_number.
        """
        with self.lock:
            return self.__workout_tables[table_id] \
                .pages[page_name][week_number].workouts[workout_number]

    def get_week_number(self, table_id, page_name):
        """
        Returns number of weeks in the plan with page_name in table with
        table_id.
        """
        with self.lock:
            return len(self.__workout_tables[table_id].pages[page_name])

    def get_workout_number(self, table_id, page_name, week_number):
        """
        Returns number of workouts in the plan with page_name in table with
        table_id in a week with week_number.
        """
        with self.lock:
            return len(self.__workout_tables[table_id]
                       .pages[page_name][week_number]
                       .workouts)
