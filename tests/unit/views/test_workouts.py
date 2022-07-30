from workout_bot.data_model.workout_plans import Excercise
from workout_bot.data_model.workout_plans import Set
from workout_bot.data_model.workout_plans import Workout
from workout_bot.view.workouts import set_to_text_message
from workout_bot.view.workouts import workout_to_text_message


class StubDataModel:
    excercise_links = {}


data_model = StubDataModel()


def test_set_to_text_message():
    """Prints sets with rounds"""

    excercise1 = Excercise("squats", "15 times")
    excercise2 = Excercise("plank", "1 minute")
    excercise3 = Excercise("stretching")
    set = Set("take a rest", 1, [excercise1, excercise2, excercise3], 3)
    expected = (
        "\nСет 1, количество раундов: 3\n"
        "take a rest\n"
        "\\- squats, 15 times\n"
        "\\- plank, 1 minute\n"
        "\\- stretching\n"
    )
    assert expected == set_to_text_message(data_model, set)


def test_set_no_rounds_to_text_message():
    """Prints sets without rounds and without description"""

    set = Set("", 2, [Excercise("treadmill")])
    expected = (
        "\nСет 2\n"
        "\\- treadmill\n"
    )
    assert expected == set_to_text_message(data_model, set)


def test_workout_to_text_message():
    """Prints workout"""

    set = Set("", 1, [Excercise("stretching")])
    workout = Workout("first workout", [set], 1, 1)

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

    set1 = Set("", 1, [Excercise("stretching")])
    set2 = Set("", 2, [Excercise("treadmill")])
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
