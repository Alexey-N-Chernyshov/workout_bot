from .utils import escape_text


def excercise_to_text_message(data_model, excercise):
    text = "- {}".format(excercise.description)
    if excercise.reps_window:
        text += ", {}".format(excercise.reps_window)
    text += "\n"
    text = escape_text(text)
    for name, link in data_model.excercise_links.items():
        if name in text:
            text = text.replace(name, "[{}]({})".format(name, link))
            break
    return text


def set_to_text_message(data_model, set):
    text = ""
    if set.number != 0:
        text += "\nСет {}".format(set.number)
    if set.rounds:
        text += escape_text(", количество раундов: {}".format(set.rounds))
    text += '\n'
    if set.description:
        text += escape_text('{}\n'.format(set.description))
    for excercise in set.excersises:
        text += excercise_to_text_message(data_model, excercise)
    return text


def workout_to_text_message(data_model, workout):
    text = ""
    if workout.number == 0:
        text = "*Промежуточная тренировка*\n"
    else:
        text = "*Тренировка {}*\n".format(workout.number)
    if workout.description:
        text += escape_text(
            "\n{}\n".format(workout.description.replace('\n', ' ')))
    for set in workout.sets:
        text += set_to_text_message(data_model, set)
    return text


def get_workout_text_message(data_model, table_id, page_name, week_number,
                             workout_number):
    workout = (
        data_model.workout_plans
        .get_workout(table_id, page_name, week_number, workout_number)
    )
    text = workout_to_text_message(data_model, workout)
    return text


def get_week_routine_text_message(data_model, table_id, page_name,
                                  week_number):
    week_routine = (
        data_model.workout_plans
        .get_week_routine(table_id, page_name, week_number)
    )
    text = "*" + \
           escape_text("Неделя {} - {}".format(week_routine.start_date,
                                               week_routine.end_date)) + \
           "*\n"
    if week_routine.comment:
        text += escape_text(week_routine.comment + "\n\n")
    workout_number = 0
    homework_number = 0
    for workout in week_routine.workouts:
        if workout.number == 0:
            homework_number += 1
        else:
            workout_number += 1
    text += "Тренировок: {}\n".format(workout_number)
    text += "Промежуточных тренировок: {}\n".format(homework_number)
    return text
