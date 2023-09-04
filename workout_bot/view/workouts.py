"""
Representation of workouts.
"""

from .utils import escape_text


def exercises_to_text_message(data_model, exercise):
    """
    Returns single exercise text representation.
    """

    text = f"- {exercise.description}"
    if exercise.reps_window:
        text += f", {exercise.reps_window}"
    if exercise.weight:
        text += f", вес {exercise.weight}"
    text += "\n"
    text = escape_text(text)
    # Exercise links ordered by length, the longest first.
    # Find the longest match.
    exercise_links = sorted(
        list(data_model.exercise_links.get_exercise_links().items()),
        key=lambda key: len(key[0]),
        reverse=True
    )
    for name, link in exercise_links:
        name = escape_text(name.lower())
        if name in text.lower():
            index_name = text.lower().index(name)
            # preserve actual case in string
            actual_name = text[index_name:index_name + len(name)]
            link = f"[{actual_name}]({escape_text(link)})"
            text = text[:index_name] + link + text[index_name + len(name):]
            break
    return text


def set_to_text_message(data_model, workout_set):
    """
    Returns workout set text representation.
    """

    text = ""
    if workout_set.number != 0:
        text += f"\nСет {workout_set.number}"
    if workout_set.rounds:
        text += escape_text(f", количество раундов: {workout_set.rounds}")
    text += '\n'
    if workout_set.description:
        text += escape_text(f"{workout_set.description}\n")
    for exercises in workout_set.exercises:
        text += exercises_to_text_message(data_model, exercises)
    return text


def workout_to_text_message(data_model, workout):
    """
    Returns workout text representation.
    """

    if workout.number == 0:
        text = "*Дополнительная тренировка*\n"
    else:
        text = f"*Тренировка {workout.number}*\n"
    if workout.description:
        text += escape_text(
            "\n{}\n".format(workout.description.replace('\n', ' ')))
    for workout_set in workout.sets:
        text += set_to_text_message(data_model, workout_set)
    return text


def get_workout_text_message(data_model, table_id, page_name, week_number,
                             workout_number):
    """
    Returns workout text representation by it ids.
    """

    workout = (
        data_model.workout_plans
        .get_workout(table_id, page_name, week_number, workout_number)
    )
    text = workout_to_text_message(data_model, workout)
    return text


def get_week_routine_text_message(data_model, table_id, page_name,
                                  week_number):
    """
    Returns short week routine representation.
    """

    week_routine = data_model.workout_plans \
        .get_week_routine(table_id, page_name, week_number)
    text = "*" + \
           escape_text(f"{page_name}\n") + \
           escape_text(f"Неделя {week_routine.start_date} -"
                       f" {week_routine.end_date}") + \
           "*\n"
    if week_routine.comment:
        text += escape_text(week_routine.comment + "\n\n")
    workout_number = 0
    additional_workout_number = 0
    for workout in week_routine.workouts:
        if workout.number == 0:
            additional_workout_number += 1
        else:
            workout_number += 1
    text += f"Тренировок: {workout_number}\n"
    if additional_workout_number != 0:
        text += f"Дополнительных тренировок: {additional_workout_number}\n"
    return text
