import re
from datetime import date
from data_model.workout_plans import Excercise
from data_model.workout_plans import Set
from data_model.workout_plans import Workout
from data_model.workout_plans import WorkoutTable
from data_model.workout_plans import WeekRoutine
from . import google_sheets_feeder


def load_workouts(workout_plans, tables):
    """
    Updates workout plans from google spreadsheet tables.
    tables - {table_id: str : [page_name]}
    """

    print('Updating workouts')
    for spreadsheet_id, pagenames in tables.get_tables().items():
        table = WorkoutTable(spreadsheet_id, "", {})
        for pagename in pagenames:
            text = (
                "Loading "
                "https://docs.google.com/spreadsheets/d/"
                f"{spreadsheet_id}/edit#gid=0 - \"{pagename}\""
            )
            print(text)
            (tablename, pagename, all_weeks) = load_table_page(spreadsheet_id,
                                                               pagename)
            table.table_name = tablename
            table.pages[pagename] = all_weeks
            print(f'Loaded "{tablename}" - "{pagename}"')
        workout_plans.update_workout_table(table)
    print('Updated workouts')


def load_table_page(spreadsheet_id, pagename):
    """
    Parses google spreadsheet page with a training program.
    Parses cell merges to determine workouts and sets.

    Retruns (tablename, pagename, list_of_week_workouts)
    """

    (tablename, merges, values) = \
        google_sheets_feeder.get_values(spreadsheet_id, pagename)
    start_week_date = date.today()
    end_week_date = date.today()
    week_comment = ""
    week_workouts = []
    workout_number = 0  # workout number in a week written in sheets
    workout_actual_number = 0  # actual workout number including homework
    workout_description = ''
    workout_sets = []
    set_number = 0
    set_rounds = 0
    set_description = ''
    set_excercises = []

    week_indeces = []
    workout_indeces = []
    for merge in merges:
        if merge["startColumnIndex"] == 0 and merge["endColumnIndex"] == 1:
            start_week_index = merge['startRowIndex'] - 1
            end_week_index = merge['endRowIndex'] - 1
            week_indeces.append((start_week_index, end_week_index))
        if merge["startColumnIndex"] == 1 and merge["endColumnIndex"] == 2:
            start_workout_index = merge["startRowIndex"] - 1
            end_workout_index = merge["endRowIndex"] - 1
            workout_indeces.append((start_workout_index, end_workout_index))
    week_indeces.sort()
    workout_indeces.sort()

    workout_num = 0
    i = 0
    while i < len(values):
        if i < workout_indeces[workout_num][0]:
            workout_indeces.append((i, i + 1))
            workout_indeces.sort()
            i += 1
        else:
            i = workout_indeces[workout_num][1]
        workout_num += 1

    all_weeks = []
    current_week = 0
    current_workout = 0
    for i in range(len(values)):
        row = values[i]

        # Set
        print(row)
        if len(row) > 2 and re.match(r"^\d+\\", row[2]):
            # it is a set description if starts with set number
            # if set_number != 0:
            workout_sets.append(Set(set_description, set_number,
                                        set_excercises, set_rounds))
            print(f"clear set_excercises={set_excercises}")
            set_excercises = []
            number, rest = row[2].split('\\', 1)
            set_number = int(number)
            # read rounds if present
            if rest[0].isdigit():
                if '\\' in rest:
                    rounds, rest = rest.split('\\', 1)
                    set_rounds = rounds
                else:
                    set_rounds = rest
                    rest = ""
            else:
                set_rounds = 0
            set_description = rest
        else:
            # it is an excercise
            if len(row) >= 4:
                # excercise reps present
                set_excercises.append(Excercise(row[2], row[3]))
            elif len(row) >= 3:
                # excercise reps not present
                set_excercises.append(Excercise(row[2]))
            # otherwise empty string - no excercise

        # workout begin
        if i == workout_indeces[current_workout][0]:
            print(f"workout begin {i}")

            workout_sets = []
            workout_actual_number += 1
            # check workout type
            if row[1] and row[1][0].isdigit():
                # it's a workout
                num, workout_description = \
                    re.split(r"(^\d+)", row[1], maxsplit=1)[1:]
                workout_number = int(num)
            else:
                # it's a homework
                workout_number = 0
                workout_description = row[1]

        # week begin
        if i == week_indeces[current_week][0]:
            print(f"week begin {i}")

            week_workouts = []
            days, rest = row[0].strip().split('.', 1)
            start_day, end_day = [int(x) for x in days.split('-')]
            month, week_comment = re.split(r"(^\d+)", rest, maxsplit=1)[1:]
            end_month = int(month)
            start_year = date.today().year
            end_year = date.today().year
            if start_day > end_day:
                start_month = end_month - 1
                if start_month == 0:
                    start_month = 12
                    start_year -= 1
            else:
                start_month = end_month
            start_week_date = date(start_year, start_month, start_day)
            end_week_date = date(end_year, end_month, end_day)

        # Workout end
        print(f"check workout end {i} == {workout_indeces[current_workout][1] - 1}")
        if (i == workout_indeces[current_workout][1] - 1
                or i == len(values) - 1):
            print(f"workout end {i}")
            workout_sets.append(Set(set_description, set_number,
                                    set_excercises, set_rounds))
            week_workouts.append(Workout(workout_description, workout_sets,
                                         workout_actual_number,
                                         workout_number))
            set_excercises = []
            workout_sets = []
            set_number = 0
            set_description = ''
            set_rounds = 0
            workout_description = ''
            current_workout += 1

        # week end
        if (i == week_indeces[current_week][1] - 1
                or i == len(values) - 1):
            print(f"week end {i}")
            all_weeks.append(WeekRoutine(start_week_date, end_week_date,
                                         current_week + 1, week_workouts,
                                         week_comment.strip()))
            workout_actual_number = 0
            current_week += 1

    return tablename, pagename, all_weeks
