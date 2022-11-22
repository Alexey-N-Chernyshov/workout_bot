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
raw_table_data = (
    "Копия спортсмены по вечерам",
    [
        {'sheetId': 900614298, 'startRowIndex': 1, 'endRowIndex': 34, 'startColumnIndex': 0, 'endColumnIndex': 1},
        {'sheetId': 900614298, 'startRowIndex': 1, 'endRowIndex': 12, 'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 900614298, 'startRowIndex': 12, 'endRowIndex': 23, 'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 900614298, 'startRowIndex': 23, 'endRowIndex': 34, 'startColumnIndex': 1, 'endColumnIndex': 2}
    ],
    [
        ['01-07.08'],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        ['', '2\n60-70%\n сначал гимнастику с палкой', '1\\2\\'],
        ['', '', 'тяга гантели к бедру', '15/15'],
        ['', '', 'становая тяга', '10'], ['', '', '2\\2\\'],
        ['', '', 'жим гантелей лежа под угом вверх', '15'],
        ['', '', 'присед с гирей', '10'],
        ['', '', '3\\выполнить максимум раундов за 10минут (веса средне-легкие)\nпримерно 3-4 круга'],
        ['', '', 'махи гирей', '5'],
        ['', '', 'диагональная складка', '10'],
        ['', '', 'броски мяча ', '5'],
        ['', '', 'подтягивания на петлях к поясу', '10'],
        ['', '', '1\\3'],
        ['', '', 'жим сидя в тренажере', '10'],
        ['', '', 'Болгарские выпады ', '10/10'],
        ['', '', '2\\3'],
        ['', '', 'подтягивания  \\тяга вертикального блока', '8'],
        ['', '', 'обратная экстензия с весом', '10-15'],
        ['', '', '2\\выполнить максимум раундов за 10 минут (веса средне-легкие)\nпримерно 3-4 круга'],
        ['', '', 'выпады шагами', '10'], ['', '', 'диагональная складка', '10'],
        ['', '', 'гребля', '10 калорий'],
        ['', '', 'подтягивания на петлях к плечам', '10']
    ]
)

expected_workouts = [
    WeekRoutine(start_date=datetime.date(2022, 8, 1),
                end_date=datetime.date(2022, 8, 7),
                number=1,
                workouts=[
                    Workout(description='\n60-70%\n сначал гимнастику с палкой',
                            sets=[
                                Set(description='',
                                    number=1,
                                    exercises=[
                                        Exercise(description='тяга гантели к бедру', reps_window='15/15'),
                                        Exercise(description='становая тяга', reps_window='10')
                                    ],
                                    rounds='2'),
                                Set(description='',
                                    number=2,
                                    exercises=[
                                        Exercise(description='жим гантелей лежа под угом вверх', reps_window='15'),
                                        Exercise(description='присед с гирей', reps_window='10')
                                    ],
                                    rounds='2'),
                                Set(description='выполнить максимум раундов за 10минут (веса средне-легкие)\nпримерно 3-4 круга',
                                    number=3,
                                    exercises=[
                                        Exercise(description='махи гирей', reps_window='5'),
                                        Exercise(description='диагональная складка', reps_window='10'),
                                        Exercise(description='броски мяча', reps_window='5'),
                                        Exercise(description='подтягивания на петлях к поясу', reps_window='10')
                                    ],
                                    rounds=0
                                    )
                            ],
                            actual_number=1,
                            number=2
                            ),
                    Workout(description='',
                            sets=[
                                Set(description='',
                                    number=1,
                                    exercises=[
                                        Exercise(description='жим сидя в тренажере', reps_window='10'),
                                        Exercise(description='Болгарские выпады', reps_window='10/10')
                                    ],
                                    rounds='3'
                                    ),
                                Set(description='',
                                    number=2,
                                    exercises=[
                                        Exercise(description='подтягивания  \\тяга вертикального блока', reps_window='8'),
                                        Exercise(description='обратная экстензия с весом', reps_window='10-15')
                                    ],
                                    rounds='3'
                                    ),
                                Set(description='выполнить максимум раундов за 10 минут (веса средне-легкие)\nпримерно 3-4 круга',
                                    number=2,
                                    exercises=[
                                        Exercise(description='выпады шагами', reps_window='10'),
                                        Exercise(description='диагональная складка', reps_window='10'),
                                        Exercise(description='гребля', reps_window='10 калорий'),
                                        Exercise(description='подтягивания на петлях к плечам', reps_window='10')
                                    ],
                                    rounds=0
                                    )
                            ],
                            actual_number=2,
                            number=0)
                ],
                comment=''
                )
]