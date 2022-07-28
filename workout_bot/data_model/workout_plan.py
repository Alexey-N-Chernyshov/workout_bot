import threading
from datetime import date
from dataclasses import dataclass
from typing import List
from typing import Dict

# {name: link}
excercise_links = {}

def escape_text(text):
    """
    Escape text for MarkdownV2
    """
    text = text.replace('\\', '\\\\')
    text = text.replace('(', '\\(')
    text = text.replace(')', '\\)')
    text = text.replace('-', '\\-')
    text = text.replace('+', '\\+')
    text = text.replace('.', '\\.')
    text = text.replace('=', '\\=')
    return text


@dataclass
class Excercise:
    description: str
    reps_window: str = ''

    def to_text_message(self):
        text = "- {}".format(self.description)
        if self.reps_window:
            text += ", {}".format(self.reps_window)
        text += "\n"
        text = escape_text(text)
        for name, link in excercise_links.items():
            if name in text:
                text = text.replace(name, "[{}]({})".format(name, link))
                break
        return text


@dataclass
class Set:
    description: str
    number: int
    excersises: List[Excercise]
    rounds: str = ""

    def to_text_message(self):
        text = "\nСет {}".format(self.number)
        if self.rounds:
            text += escape_text(", количество раундов: {}".format(self.rounds))
        text += '\n'
        if self.description:
            text += escape_text('{}\n'.format(self.description))
        for excercise in self.excersises:
            text += excercise.to_text_message()
        return text


@dataclass
class Workout:
    description: str
    sets: List[Set]
    actual_number: int
    number: int = 0

    def to_text_message(self):
        text = ""
        if self.number == 0:
            text = "*Промежуточная тренировка*\n"
        else:
            text = "*Тренировка {}*\n".format(self.number)
        if self.description:
            text += escape_text(
                "\n{}\n".format(self.description.replace('\n', ' ')))
        for set in self.sets:
            text += set.to_text_message()
        return text


@dataclass
class WeekRoutine:
    start_date: date
    end_date: date
    number: int
    workouts: List[Workout]
    comment: str

    def to_text_message(self):
        text = "*" + \
               escape_text("Неделя {} - {}".format(self.start_date,
                                                   self.end_date)) + \
               "*\n"
        if self.comment:
            text += escape_text(self.comment + "\n\n")
        workout_number = 0
        homework_number = 0
        for workout in self.workouts:
            if workout.number == 0:
                homework_number += 1
            else:
                workout_number += 1
        text += "Тренировок: {}\n".format(workout_number)
        text += "Промежуточных тренировок: {}\n".format(homework_number)
        return text


@dataclass
class WorkoutTable:
    table_id: str
    table_name: str
    pages: Dict[str, List[WeekRoutine]]


class WorkoutLibrary:
    """
    Thread-safe workout storage
    """
    # map {table_id -> WorkoutTable}
    __workout_tables = {}
    lock = threading.Lock()

    def update_workout_table(self, workout_table):
        self.lock.acquire()
        self.__workout_tables[workout_table.table_id] = workout_table
        self.lock.release()

    def get_plan_names(self):
        plans = []
        self.lock.acquire()
        for table in self.__workout_tables.values():
            for pagename in table.pages.keys():
                plans.append(table.table_name + " - " + pagename)
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

    def get_workout_text_message(self, table_id, page_name, week_number,
                                 workout_number):
        self.lock.acquire()
        text = self.__workout_tables[table_id].pages[page_name][week_number] \
            .workouts[workout_number].to_text_message()
        self.lock.release()
        return text

    def get_week_text_message(self, table_id, page_name, week_number):
        self.lock.acquire()
        text = self.__workout_tables[table_id].pages[page_name][week_number] \
            .to_text_message()
        self.lock.release()
        return text

    def get_week_number(self, table_id, page_name):
        self.lock.acquire()
        week_number = len(self.__workout_tables[table_id].pages[page_name])
        self.lock.release()
        return week_number

    def get_workout_number(self, table_id, page_name, week_number):
        self.lock.acquire()
        workout_number = \
            len(self.__workout_tables[table_id].pages[page_name][week_number] \
            .workouts)
        self.lock.release()
        return workout_number
