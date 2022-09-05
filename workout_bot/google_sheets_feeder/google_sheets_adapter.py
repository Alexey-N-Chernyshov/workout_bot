"""
Transforms loaded Google spreadsheets into data model.
"""

import re
from datetime import date
from data_model.workout_plans import Excercise
from data_model.workout_plans import Set
from data_model.workout_plans import Workout
from data_model.workout_plans import WeekRoutine


class GoogleSheetsAdapter:
    """
    Parses google sheets raw data and transforms to data model format.
    """

    def parse_excercise_links(self, values):
        """
        Loads excercise links from google table.

        Returns excercises sorted by name length in reverse order.
        """

        return sorted(filter(lambda item: item, values),
                      key=lambda x: len(x[0]),
                      reverse=True)


    def parse_merges(self, merges):
        """
        Parses merges in order to determine week indeces (begins and ends).
        """

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
                workout_indeces.append((start_workout_index,
                                        end_workout_index))
        week_indeces.sort()
        workout_indeces.sort()

        return (week_indeces, workout_indeces)


    def parse_week_begin(self, to_parse):
        """
        Parses week description.
        Returns week start date, end date, comment for the week.
        """

        days, rest = to_parse.strip().split('.', 1)
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

        return (start_week_date, end_week_date, week_comment)


    def parse_workout(self, to_parse):
        """
        Parses single workout.
        Returns workout number and description.
        """

        if to_parse and to_parse[0].isdigit():
            # it's a workout
            num, workout_description = \
                re.split(r"(^\d+)", to_parse, maxsplit=1)[1:]
            workout_number = int(num)
        else:
            # it's a homework
            workout_number = 0
            workout_description = to_parse
        return (workout_number, workout_description)


    def parse_table_page(self, merges, values):
        """
        Parses google spreadsheet page with a training program.
        Parses cell merges to determine workouts and sets.

        Retruns list_of_week_workouts
        """

        start_week_date = date.today()
        end_week_date = date.today()
        week_comment = ""
        week_workouts = []
        workout = Workout("", [], 0)
        workout_actual_number = 0  # actual workout number including homework
        set_number = 0
        set_rounds = 0
        set_description = ''
        set_excercises = []

        week_indeces, workout_indeces = self.parse_merges(merges)

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
        for i, row in enumerate(values):
            # Set
            if len(row) > 2 and re.match(r"^\d+\\", row[2]):
                # it is a set description if starts with set number
                # if set_number != 0:
                workout.sets.append(Set(set_description, set_number,
                                        set_excercises, set_rounds))
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
                    set_excercises.append(Excercise(row[2].strip(),
                                                    row[3].strip()))
                elif len(row) >= 3:
                    # excercise reps not present
                    set_excercises.append(Excercise(row[2].strip()))
                # otherwise empty string - no excercise

            # workout begin
            if i == workout_indeces[current_workout][0]:
                workout.sets = []
                workout_actual_number += 1
                # check workout type
                workout.number, workout.description = \
                    self.parse_workout(row[1])

            # week begin
            if i == week_indeces[current_week][0]:
                week_workouts = []
                start_week_date, end_week_date, week_comment = \
                    self.parse_week_begin(row[0])

            # Workout end
            if i in (workout_indeces[current_workout][1] - 1, len(values) - 1):
                workout.sets.append(Set(set_description, set_number,
                                        set_excercises, set_rounds))
                workout.actual_number = workout_actual_number
                week_workouts.append(workout)
                workout = Workout("", [], 0)
                set_excercises = []
                set_number = 0
                set_description = ''
                set_rounds = 0
                current_workout += 1

            # week end
            if i in (week_indeces[current_week][1] - 1, len(values) - 1):
                all_weeks.append(WeekRoutine(start_week_date, end_week_date,
                                             current_week + 1, week_workouts,
                                             week_comment.strip()))
                workout_actual_number = 0
                current_week += 1

        return all_weeks
