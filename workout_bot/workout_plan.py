import threading
from datetime import date
from dataclasses import dataclass
from typing import List


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
    return text


@dataclass
class Excercise:
    description: str
    reps_window: str = ''

    def to_text_message():
        text = ""
        if excercise.reps_window:
            text += escape_text("\n- {}, {}"
                                .format(excercise.description,
                                        excercise.reps_window))
        else:
            text += escape_text("\n- {}"
                                .format(excercise.description))
        return text


@dataclass
class Set:
    description: str
    number: int
    excersises: List[Excercise]
    rounds: int = 0

    def to_text_message(self):
        text = "Сет {}".format(self.number)
        if self.rounds != 0:
            text += ', количество раундов: {}'.format(self.rounds)
        if self.description:
            text += escape_text('\n{}'.format(self.description))
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
        text = ''
        if self.number == 0:
            text = '*Промежуточная тренировка*\n\n'
        else:
            text = '*Тренировка {}*\n\n'.format(self.number)
        if self.description:
            text += escape_text(
                '{}\n\n'.format(self.description.replace('\n', ' ')))
        for set in self.sets:
            text += set.to_text_message()
        return text


@dataclass
class WeekRoutine:
    start_date: date
    end_date: date
    number: int
    workouts: List[Workout]

    def to_text_message(self):
        text = "*" + \
               escape_text("Неделя {} - {}\n".format(self.start_date,
                                                     self.end_date)) + \
               "*"
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


class WorkoutLibrary:
    """
    Thread-safe workout storage
    """
    # workout plan name -> List[WeekRoutine]
    __workout_plans = {}
    lock = threading.Lock()

    def update_workout_plans(self, workout_plans):
        self.lock.acquire()
        self.__workout_plans = workout_plans
        self.lock.release()

    def get_plan_names(self):
        self.lock.acquire()
        plans = self.__workout_plans.keys()
        self.lock.release()
        return plans

    def get_workout_text_message(self, workout_plan, week_number,
                                 workout_number):
        self.lock.acquire()
        text = self.__workout_plans[workout_plan][week_number] \
            .workouts[workout_number].to_text_message()
        self.lock.release()
        return text

    def get_week_text_message(self, workout_plan, week_number):
        self.lock.acquire()
        text = self.__workout_plans[workout_plan][week_number] \
            .to_text_message()
        self.lock.release()
        return text

    def get_week_number(self, workout_plan):
        self.lock.acquire()
        week_number = len(self.__workout_plans[workout_plan])
        self.lock.release()
        return week_number

    def get_workout_number(self, workout_plan, week_number):
        self.lock.acquire()
        workout_number = \
            len(self.__workout_plans[workout_plan][week_number].workouts)
        self.lock.release()
        return workout_number
