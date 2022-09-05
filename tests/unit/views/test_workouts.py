"""
Tests for workout representation.
"""

from dataclasses import dataclass
from workout_bot.data_model.workout_plans import Exercise
from workout_bot.data_model.workout_plans import Set
from workout_bot.data_model.workout_plans import Workout
from workout_bot.view.workouts import set_to_text_message
from workout_bot.view.workouts import workout_to_text_message


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

    exercise_links = StubExerciseLinks()


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
        "*Промежуточная тренировка*\n"
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
