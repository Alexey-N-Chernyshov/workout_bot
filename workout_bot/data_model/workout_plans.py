"""
Provides access to workouts and plans.
"""

import threading
from datetime import date
from dataclasses import dataclass
from typing import List
from typing import Dict


@dataclass
class Excercise:
    """
    Is a single excercise.
    """

    description: str
    reps_window: str = ''


@dataclass
class Set:
    """
    Is a set of excercises.
    """

    description: str
    number: int
    excersises: List[Excercise]
    rounds: str = ""


@dataclass
class Workout:
    """
    Single workout consists of excercises combined into sets.
    """

    description: str
    sets: List[Set]
    actual_number: int
    number: int = 0


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
    # map {table_id -> WorkoutTable}
    __workout_tables = {}
    lock = threading.Lock()

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

    def is_plan_present(self, table_id, plan):
        """
        Checks if table with table_id has page named plan.
        """

        return plan in self.get_plan_names(table_id)

    def get_plan_names(self, table_id):
        """
        Returns all plans for a table with table_id.
        """

        plans = []
        with self.lock:
            if table_id in self.__workout_tables:
                table = self.__workout_tables[table_id]
                for pagename in table.pages.keys():
                    plans.append(pagename)
            return plans

    def get_plan_name(self, table_id):
        """
        Returns talbe name for table with table_id.
        """

        name = None
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
