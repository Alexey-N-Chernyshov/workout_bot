"""
Transforms loaded Google spreadsheets into data model.
"""

import re
from datetime import date
from data_model.workout_plans import (
    Exercise, Set, WeekRoutine, Workout
)


class GoogleSheetsAdapter:
    """
    Parses google sheets raw data and transforms to data model format.
    """

    def parse_exercise_links(self, values):
        """
        Loads exercise links from Google table.

        Returns exercise list sorted by length of name in reverse order.
        """

        return dict(filter(lambda item: (item and len(item) == 2), values))

    def parse_merges(self, merges, values):
        """
        Parses merges in order to determine week indexes (begins and ends).
        """

        # list of weeks index pairs (begin, end)
        week_indexes = []
        # list of workout index pairs (begin, end)
        day_indexes = []

        for merge in merges:
            if merge["startColumnIndex"] == 0 and merge["endColumnIndex"] == 1:
                start_week_index = merge['startRowIndex'] - 1
                end_week_index = merge['endRowIndex'] - 1
                week_indexes.append((start_week_index, end_week_index))
            if merge["startColumnIndex"] == 1 and merge["endColumnIndex"] == 2:
                start_day_index = merge["startRowIndex"] - 1
                end_day_index = merge["endRowIndex"] - 1
                day_indexes.append((start_day_index,
                                    end_day_index))
        week_indexes.sort()
        day_indexes.sort()

        workout_num = 0
        i = 0
        while i < len(values):
            if len(day_indexes) <= workout_num \
                    or i < day_indexes[workout_num][0]:
                day_indexes.append((i, i + 1))
                day_indexes.sort()
                i += 1
            else:
                i = day_indexes[workout_num][1]
            workout_num += 1

        return week_indexes, day_indexes

    def parse_week_begin(self, to_parse):
        """
        Parses week date and comment.
        """

        dates, week_comment = re.split(
            r"(^\d{1,2}\.?\d{0,2}-\d{1,2}\.\d{1,2})",
            to_parse,
            maxsplit=1)[1:]
        start_date, end_date = dates.split('-')
        if '.' in start_date:
            start_day, start_month = [int(x) for x in start_date.split('.')]
        else:
            start_day = int(start_date)
        end_day, end_month = [int(x) for x in end_date.split('.', 1)]
        start_year = date.today().year
        end_year = date.today().year
        if start_day > end_day:
            start_month = end_month - 1
            if start_month == 0:
                start_month = 12
                end_year += 1
        else:
            start_month = end_month
        start_week_date = date(start_year, start_month, start_day)
        end_week_date = date(end_year, end_month, end_day)

        return WeekRoutine(start_week_date, end_week_date, 0, [],
                           week_comment.strip())

    def parse_workout_set(self, to_parse):
        """
        Parses description of workout set.
        """

        workout_description = to_parse[2]
        workout_set = Set("", 0, [])
        number, rest = workout_description.split('\\', 1)
        workout_set.number = int(number)
        # read rounds if present
        if rest and rest[0].isdigit():
            if '\\' in rest:
                rounds, rest = rest.split('\\', 1)
                workout_set.rounds = rounds
            else:
                workout_set.rounds = rest
                rest = ""
        else:
            workout_set.rounds = 0
        workout_set.description = rest

        # multicell set description
        if len(to_parse) > 3:
            workout_set.description += "\n"
            workout_set.description += to_parse[3]

        return workout_set

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
        return workout_number, workout_description

    def parse_table_page(self, merges, values):
        """
        Parses google spreadsheet page with a training program.
        Parses cell merges to determine workouts and sets.

        Retruns list_of_week_workouts
        """

        week_routine = WeekRoutine(date.today(), date.today(), 0, [], "")
        workout = Workout("", [], 0)
        workout_set = Set("", 0, [])
        workout_actual_number = 0  # actual workout number including homework

        week_indexes, workout_indexes = self.parse_merges(merges, values)

        all_weeks = []
        current_week = 0
        current_workout = 0
        for i, row in enumerate(values):
            # Set
            if len(row) > 2 and re.match(r"^\d+\\", row[2]):
                # it is a set description if starts with set number
                # if set_number != 0:
                workout.sets.append(workout_set)
                workout_set = self.parse_workout_set(row)
            else:
                # it is an exercise with reps window and weight
                if len(row) >= 5:
                    workout_set.exercises.append(
                        Exercise(
                            row[2].strip(),
                            row[3].strip(),
                            row[4].strip()
                        )
                    )
                # it is an exercise with reps window
                if len(row) == 4:
                    # exercise reps present
                    workout_set.exercises.append(
                        Exercise(row[2].strip(), row[3].strip())
                    )
                # it is an exercise with reps window only
                elif len(row) == 3:
                    # exercise reps not present
                    workout_set.exercises.append(Exercise(row[2].strip()))
                # otherwise empty string - no exercise

            # workout begin
            if i == workout_indexes[current_workout][0]:
                workout.sets = []
                # if not an empty workout
                if len(row) >= 2:
                    workout_actual_number += 1
                    # check workout type
                    workout.number, workout.description = \
                        self.parse_workout(row[1])

            # begin of week
            if i == week_indexes[current_week][0]:
                week_routine = self.parse_week_begin(row[0])

            # Workout end
            if i in (workout_indexes[current_workout][1] - 1, len(values) - 1):
                workout.sets.append(workout_set)
                workout_set = Set("", 0, [])
                workout.actual_number = workout_actual_number
                # if workout not empty
                if not workout.empty():
                    week_routine.workouts.append(workout)
                workout = Workout("", [], 0)
                current_workout += 1

            # end of week
            if i in (week_indexes[current_week][1] - 1, len(values) - 1):
                current_week += 1
                week_routine.number = current_week
                all_weeks.append(week_routine)
                workout_actual_number = 0

        return all_weeks
