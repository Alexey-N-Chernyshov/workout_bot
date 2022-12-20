"""
Tests for workout representation.
"""

import datetime
from dataclasses import dataclass
from workout_bot.data_model.workout_plans import Exercise
from workout_bot.data_model.workout_plans import Set
from workout_bot.data_model.workout_plans import Workout
from workout_bot.data_model.workout_plans import WeekRoutine
from workout_bot.view.workouts import set_to_text_message
from workout_bot.view.workouts import workout_to_text_message
from workout_bot.view.workouts import get_week_routine_text_message


@dataclass
class StubDataModel:
    """
    Mock for data model.
    """

    @dataclass
    class StubExerciseLinks:
        """
        Mock for exercise links.
        """

        def get_exercise_links(self):
            """
            Returns map {exercise_name: link}
            """

            return {}

    @dataclass
    class StubWorkoutPlans:
        """
        Mock workout_plans
        """

        week_routine = WeekRoutine(
            datetime.date(2022, 8, 1),
            datetime.date(2022, 8, 8),
            1,
            [Workout("first workout", [], 1, 1)],
            "comment"
        )

        def get_week_routine(self, _table_id, _page_name, _week_number):
            """
            Returns mocked week routine.
            """

            return self.week_routine

    exercise_links = StubExerciseLinks()
    workout_plans = StubWorkoutPlans()


data_model = StubDataModel()


def test_set_to_text_message():
    """Prints sets with rounds"""

    exercise1 = Exercise("squats", "15 times")
    exercise2 = Exercise("plank", "1 minute")
    exercise3 = Exercise("stretching")
    workout_set = Set("take a rest", 1,
                      [exercise1, exercise2, exercise3], 3)
    expected = (
        "\nСет 1, количество раундов: 3\n"
        "take a rest\n"
        "\\- squats, 15 times\n"
        "\\- plank, 1 minute\n"
        "\\- stretching\n"
    )
    assert expected == set_to_text_message(data_model, workout_set)


def test_set_no_rounds_to_text_message():
    """Prints sets without rounds and without description"""

    workout_set = Set("", 2, [Exercise("treadmill")])
    expected = (
        "\nСет 2\n"
        "\\- treadmill\n"
    )
    assert expected == set_to_text_message(data_model, workout_set)


def test_workout_to_text_message():
    """Prints workout"""

    workout_set = Set("", 1, [Exercise("stretching")])
    workout = Workout("first workout", [workout_set], 1, 1)

    expected = (
        "*Тренировка 1*\n"
        "\n"
        "first workout\n"
        "\n"
        "Сет 1\n"
        "\\- stretching\n"
    )
    assert expected == workout_to_text_message(data_model, workout)


def test_workout_no_number_to_text_message():
    """Prints workout without explicit number"""

    set1 = Set("", 1, [Exercise("stretching")])
    set2 = Set("", 2, [Exercise("treadmill")])
    workout = Workout("first workout", [set1, set2], 1)

    expected = (
        "*Дополнительная тренировка*\n"
        "\n"
        "first workout\n"
        "\n"
        "Сет 1\n"
        "\\- stretching\n"
        "\n"
        "Сет 2\n"
        "\\- treadmill\n"
    )
    assert expected == workout_to_text_message(data_model, workout)


def test_week_routine_test():
    """
    Tests week routine text representation.
    """

    table_id = "table_id"
    page_name = "page name"
    week_number = 1

    expected = (
        "*page name\n"
        "Неделя 2022\\-08\\-01 \\- 2022\\-08\\-08*\n"
        "comment\n"
        "\n"
        "Тренировок: 1\n"
    )
    print(get_week_routine_text_message(
        data_model, table_id, page_name, week_number))

    assert expected == get_week_routine_text_message(
        data_model, table_id, page_name, week_number)


def test_week_routine_additional_workout_test():
    """
    Tests week routine with additional workout text representation.
    """

    data_model.workout_plans.week_routine = \
        WeekRoutine(datetime.date(2022, 8, 1),
                    datetime.date(2022, 8, 8),
                    1,
                    [
                        Workout("first workout", [], 1, 1),
                        Workout("first workout", [], 2)
                    ],
                    "comment"
                    )

    table_id = "table_id"
    page_name = "page name"
    week_number = 1

    expected = (
        "*page name\n"
        "Неделя 2022\\-08\\-01 \\- 2022\\-08\\-08*\n"
        "comment\n"
        "\n"
        "Тренировок: 1\n"
        "Дополнительных тренировок: 1\n"
    )
    print(get_week_routine_text_message(
        data_model, table_id, page_name, week_number))

    assert expected == get_week_routine_text_message(
        data_model, table_id, page_name, week_number)
