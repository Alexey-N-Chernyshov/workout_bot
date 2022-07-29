import threading
from datetime import date
from dataclasses import dataclass
from typing import List
from typing import Dict


@dataclass
class Excercise:
    description: str
    reps_window: str = ''


@dataclass
class Set:
    description: str
    number: int
    excersises: List[Excercise]
    rounds: str = ""


@dataclass
class Workout:
    description: str
    sets: List[Set]
    actual_number: int
    number: int = 0


@dataclass
class WeekRoutine:
    start_date: date
    end_date: date
    number: int
    workouts: List[Workout]
    comment: str


@dataclass
class WorkoutTable:
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
        self.lock.acquire()
        self.__workout_tables[workout_table.table_id] = workout_table
        self.lock.release()

    def is_table_id_present(self, table_id):
        return table_id in self.__workout_tables

    def get_plan_names(self, table_id):
        plans = []
        self.lock.acquire()
        if table_id in self.__workout_tables:
            table = self.__workout_tables[table_id]
            for pagename in table.pages.keys():
                plans.append(pagename)
        self.lock.release()
        return plans

    def get_plan_name(self, table_id):
        name = None
        self.lock.acquire()
        if table_id in self.__workout_tables:
            name = self.__workout_tables[table_id].table_name
        self.lock.release()
        return name

    def get_table_id_by_name(self, name):
        res = None
        self.lock.acquire()
        for table_id, table in self.__workout_tables.items():
            if table.table_name == name:
                res = table_id
        self.lock.release()
        return res

    def get_week_routine(self, table_id, page_name, week_number):
        self.lock.acquire()
        week_routine = (
            self.__workout_tables[table_id]
            .pages[page_name][week_number]
        )
        self.lock.release()
        return week_routine

    def get_workout(self, table_id, page_name, week_number, workout_number):
        self.lock.acquire()
        workout = (
            self.__workout_tables[table_id]
            .pages[page_name][week_number]
            .workouts[workout_number]
        )
        self.lock.release()
        return workout

    def get_week_number(self, table_id, page_name):
        self.lock.acquire()
        week_number = len(self.__workout_tables[table_id].pages[page_name])
        self.lock.release()
        return week_number

    def get_workout_number(self, table_id, page_name, week_number):
        self.lock.acquire()
        workout_number = \
            len(self.__workout_tables[table_id].pages[page_name][week_number]
                .workouts)
        self.lock.release()
        return workout_number
