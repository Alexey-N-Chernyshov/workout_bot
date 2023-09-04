"""
Test data from Google spreadsheets.
One exercise per line.
"""

import datetime
from workout_bot.data_model.workout_plans import (
    Exercise,
    Set,
    Workout,
    WeekRoutine,
)

# No Quality Assurance for the test data file.
# flake8: noqa

# Raw data loaded from Google Spreadsheet:
# - table name
# - cell merges
# - data
RAW_TABLE_DATA_ONE_EXERCISE_PER_LINE = (
    "Название страницы",
    [
        {'sheetId': 900614298, 'startRowIndex': 1, 'endRowIndex': 6, 'startColumnIndex': 0, 'endColumnIndex': 1},
        {'sheetId': 900614298, 'startRowIndex': 3, 'endRowIndex': 6, 'startColumnIndex': 1, 'endColumnIndex': 2}
    ],
    [
        ['29-04.09', '1', 'экстензия ', '75 (набрать за минимум подходов)'],
        ['', '2', 'легкий\\средний бег', '1 км'],
        ['', '3\n60-75%', '1\\4\\'],
        ['', '', 'подтягивания ', '8-10'],
        ['', '', 'приседания со штангой на спине', '8-10', '45-50']
    ]
)

EXPECTED_ONE_EXERCISE_PER_LINE = [
    WeekRoutine(
        start_date=datetime.date(2022, 8, 29),
        end_date=datetime.date(2022, 9, 4),
        number=1,
        workouts=[
            Workout(
                description="",
                sets=[
                    Set(
                        description="",
                        number=0,
                        exercises=[
                            Exercise(description="экстензия", reps_window="75 (набрать за минимум подходов)"),
                        ],
                        rounds=""
                    ),
                ],
                actual_number=1,
                number=1
            ),
            Workout(
                description="",
                sets=[
                    Set(
                        description="",
                        number=0,
                        exercises=[
                            Exercise(description='легкий\\средний бег', reps_window="1 км"),
                        ],
                        rounds=""
                    ),
                ],
                actual_number=2,
                number=2
            ),
            Workout(
                description="\n60-75%",
                sets=[
                    Set(
                        description="",
                        number=1,
                        exercises=[
                            Exercise(description="подтягивания", reps_window="8-10"),
                            Exercise(description="приседания со штангой на спине", reps_window="8-10", weight='45-50')
                        ],
                        rounds="4"
                    ),
                ],
                actual_number=3,
                number=3
            )
        ],
        comment=""
    )
]
