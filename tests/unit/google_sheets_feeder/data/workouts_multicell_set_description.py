"""
Test data with extended set description:
+----------------------|--------------+
| 2\\3-5\\отдых 90 сек | набрать 36 п |
+----------------------+-^^^^^^^^^^^^-+
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
RAW_TABLE_DATA_MULTICELL_SET_DESCRIPTION = (
    "тест - спортсмены по вечерам",
    [
        {
            'sheetId': 900614298,
            'startRowIndex': 1,
            'endRowIndex': 16,
            'startColumnIndex': 1,
            'endColumnIndex': 2
        },
        {
            'sheetId': 900614298,
            'startRowIndex': 1,
            'endRowIndex': 16,
            'startColumnIndex': 0,
            'endColumnIndex': 1
        }
    ],
    [
        ['09-15.01\nтакая же тяжелая как тренер после праздников(', '1 70-75 %', 'легкий бег', '500 м'],
        ['', '', 'гребля', '500 м'],
        ['', '', '1\\2'],
        ['', '', 'обратная экстензия', '20'],
        ['', '', 'махи в наклоне', '15'],
        ['', '', '2\\3-5\\отдых 90 сек', 'набрать 36 п'],
        ['', '', 'подтягивания', '8-12'],
        ['', '', '3\\2-3\\отдых 90 сек', 'набрать 24 п'],
        ['', '', 'тяга штанги к поясу', '8-12'],
        ['', '', '4\\3-5\\отдых 90 сек', 'набрать 36 п'],
        ['', '', 'фронтальные приседания', '8-12'],
        ['', '', '5\\3\\минимум отдыха'],
        ['', '', 'скакалка', '30'],
        ['', '', 'ракушка', '15/15'],
        ['', '', 'комбо на пресс', 'по 10']
    ]
)


EXPECTED_WORKOUTS_MULTICELL_SET_DESCRIPTION = [
    WeekRoutine(
        start_date=datetime.date(2023, 1, 9),
        end_date=datetime.date(2023, 1, 15),
        number=1,
        workouts=[
            Workout(
                description=' 70-75 %',
                sets=[
                    Set(
                        description='',
                        number=0,
                        exercises=[
                            Exercise(
                                description='легкий бег',
                                reps_window='500 м'
                            ),
                            Exercise(
                                description='гребля',
                                reps_window='500 м'
                            )
                        ],
                        rounds=''
                    ),
                    Set(
                        description='',
                        number=1,
                        exercises=[
                            Exercise(
                                description='обратная экстензия',
                                reps_window='20'
                            ),
                            Exercise(
                                description='махи в наклоне',
                                reps_window='15'
                            )
                        ],
                        rounds='2'
                    ),
                    Set(
                        description='отдых 90 сек\nнабрать 36 п',
                        number=2,
                        exercises=[
                            Exercise(
                                description='подтягивания',
                                reps_window='8-12'
                            )
                        ],
                        rounds='3-5'
                    ),
                    Set(
                        description='отдых 90 сек\nнабрать 24 п',
                        number=3,
                        exercises=[
                            Exercise(
                                description='тяга штанги к поясу',
                                reps_window='8-12'
                            )
                        ],
                        rounds='2-3'
                    ),
                    Set(
                        description='отдых 90 сек\nнабрать 36 п',
                        number=4,
                        exercises=[
                            Exercise(
                                description='фронтальные приседания',
                                reps_window='8-12'
                            )
                        ],
                        rounds='3-5'
                    ),
                    Set(
                        description='минимум отдыха',
                        number=5,
                        exercises=[
                            Exercise(
                                description='скакалка',
                                reps_window='30'
                            ),
                            Exercise(
                                description='ракушка',
                                reps_window='15/15'
                            ),
                            Exercise(
                                description='комбо на пресс',
                                reps_window='по 10'
                            )
                        ],
                        rounds='3'
                    )
                ],
                actual_number=1,
                number=1)
        ],
        comment='такая же тяжелая как тренер после праздников('
    )
]
