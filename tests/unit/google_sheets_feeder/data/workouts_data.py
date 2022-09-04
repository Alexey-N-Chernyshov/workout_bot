import datetime
from workout_bot.data_model.workout_plans import (
    Excercise,
    Set,
    Workout,
    WeekRoutine,
)


# Raw data loaded from Google Spreadsheet:
# - table name
# - cell merges
# - data
raw_table_data = (
    "table name",
    [
        {'sheetId': 975635379, 'startRowIndex': 1, 'endRowIndex': 31,
            'startColumnIndex': 0, 'endColumnIndex': 1},
        {'sheetId': 975635379, 'startRowIndex': 1, 'endRowIndex': 11,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 11, 'endRowIndex': 21,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 21, 'endRowIndex': 31,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 32, 'endRowIndex': 43,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 44, 'endRowIndex': 55,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 56, 'endRowIndex': 67,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 68, 'endRowIndex': 77,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 78, 'endRowIndex': 87,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 88, 'endRowIndex': 97,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 97, 'endRowIndex': 108,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 108, 'endRowIndex': 120,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 120, 'endRowIndex': 130,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 130, 'endRowIndex': 141,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 223, 'endRowIndex': 235,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 235, 'endRowIndex': 247,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 247, 'endRowIndex': 259,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 259, 'endRowIndex': 271,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 271, 'endRowIndex': 282,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 282, 'endRowIndex': 295,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 295, 'endRowIndex': 307,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 307, 'endRowIndex': 320,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 141, 'endRowIndex': 153,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 153, 'endRowIndex': 164,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 164, 'endRowIndex': 176,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 176, 'endRowIndex': 187,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 187, 'endRowIndex': 199,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 199, 'endRowIndex': 211,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 211, 'endRowIndex': 223,
            'startColumnIndex': 1, 'endColumnIndex': 2},
        {'sheetId': 975635379, 'startRowIndex': 247, 'endRowIndex': 282,
            'startColumnIndex': 0, 'endColumnIndex': 1},
        {'sheetId': 975635379, 'startRowIndex': 282, 'endRowIndex': 320,
            'startColumnIndex': 0, 'endColumnIndex': 1},
        {'sheetId': 975635379, 'startRowIndex': 31, 'endRowIndex': 67,
            'startColumnIndex': 0, 'endColumnIndex': 1},
        {'sheetId': 975635379, 'startRowIndex': 67, 'endRowIndex': 97,
            'startColumnIndex': 0, 'endColumnIndex': 1},
        {'sheetId': 975635379, 'startRowIndex': 97, 'endRowIndex': 130,
            'startColumnIndex': 0, 'endColumnIndex': 1},
        {'sheetId': 975635379, 'startRowIndex': 130, 'endRowIndex': 153,
            'startColumnIndex': 0, 'endColumnIndex': 1},
        {'sheetId': 975635379, 'startRowIndex': 153, 'endRowIndex': 187,
            'startColumnIndex': 0, 'endColumnIndex': 1},
        {'sheetId': 975635379, 'startRowIndex': 187, 'endRowIndex': 211,
            'startColumnIndex': 0, 'endColumnIndex': 1},
        {'sheetId': 975635379, 'startRowIndex': 211, 'endRowIndex': 247,
            'startColumnIndex': 0, 'endColumnIndex': 1}
    ],
    [
        [
            "27-03.07",
            "1 \n"
            "вес примерно 85%+ от ПМ\n"
            "последние 2 тяжелые, запас в 1-2 повторения",
            '1\\3\\по готовности'
        ],
        ['', '', 'подтягивания', '3-5'],
        ['', '', 'приседания со штангой на спине', '3'],
        ['', '', '2\\3\\по готовности'],
        ['', '', 'жим штанги лежа', '3-5'],
        ['', '', 'фронтальные приседания', '3'],
        ['', '', '3\\2\\с минимум отдыха'],
        ['', '', 'тяга горизонтального блока', '3-5'],
        ['', '', 'обратная экстензия', '20'],
        ['', '', 'подъем гантелей на бицепс лежа под 45', '8-10'],
        [
            '',
            "2\n"
            "вес примерно 85%+ от ПМ\n"
            "последние 2 тяжелые, запас в 1-2 повторения",
            '1\\3\\по готовности'
        ],
        ['', '', 'отжимания на брусьях', '3-5'],
        ['', '', 'становая тяга', '3-5'],
        ['', '', '2\\3\\по готовности'],
        ['', '', 'ходьба на руках с опрой на партнера', 'по 10 шагов'],
        ['', '', 'тяга горизонтального блока', '3-5'],
        ['', '', '3\\2\\с минимум отдыха'],
        ['', '', 'треп-3 лежа под углом 30', '15'],
        ['', '', 'обратная экстензия', '20'],
        ['', '', 'комбо на пресс', 'по 20'],
        [
            '',
            "3 \n"
            "вес примерно 85%+ от ПМ\n"
            "последние 2 тяжелые, запас в 1-2 повторения",
            '1\\3\\по готовности'
        ],
        ['', '', 'подтягивания', '3-5'],
        ['', '', 'приседания со штангой на спине', '3'],
        ['', '', '2\\3\\по готовности'],
        ['', '', 'жим штанги лежа', '3-5'],
        ['', '', 'фронтальные приседания', '3'],
        ['', '', '3\\2\\с минимум отдыха'],
        ['', '', 'тяга горизонтального блока', '3-5'],
        ['', '', 'обратная экстензия', '20'],
        ['', '', 'подъем гантелей на бицепс лежа под 45', '8-10']
    ]
)


expected_workouts = [
# noqa
WeekRoutine(start_date=datetime.date(2022, 6, 27),
            end_date=datetime.date(2022, 7, 3),
            number=1,
            workouts=[
Workout(description=" \n"
                    "вес примерно 85%+ от ПМ\n"
                    "последние 2 тяжелые, запас в 1-2 повторения",
        sets=[
            Set(description='по готовности',
                number=1,
                excersises=[
                    Excercise(description='подтягивания',
                              reps_window='3-5'),
                    Excercise(description="приседания со штангой на спине",
                              reps_window='3')
                ],
                rounds='3'
                ),
            Set(description='по готовности',
                number=2,
                excersises=[
                    Excercise(description='жим штанги лежа',
                              reps_window='3-5'),
                    Excercise(description='фронтальные приседания',
                              reps_window='3')
                ],
                rounds='3'
                ),
            Set(description='с минимум отдыха',
                number=3,
                excersises=[
                    Excercise(description='тяга горизонтального блока',
                              reps_window='3-5'),
                    Excercise(description='обратная экстензия',
                              reps_window='20'),
                    Excercise(description="подъем гантелей на бицепс лежа "
                                          "под 45",
                              reps_window='8-10')
                    ],
                rounds='2')
            ],
        actual_number=1,
        number=1),
Workout(description="\n"
                    "вес примерно 85%+ от ПМ\n"
                    "последние 2 тяжелые, запас в 1-2 повторения",
        sets=[
            Set(description='по готовности',
                number=1,
                excersises=[
                    Excercise(description='отжимания на брусьях',
                              reps_window='3-5'),
                    Excercise(description='становая тяга',
                              reps_window='3-5')
                ],
                rounds='3'),
            Set(description='по готовности',
                number=2,
                excersises=[
                    Excercise(description="ходьба на руках с опрой на "
                                          "партнера",
                              reps_window='по 10 шагов'),
                    Excercise(description='тяга горизонтального блока',
                              reps_window='3-5')
                ],
                rounds='3'),
            Set(description='с минимум отдыха',
                number=3,
                excersises=[
                    Excercise(description='треп-3 лежа под углом 30',
                              reps_window='15'),
                    Excercise(description='обратная экстензия',
                              reps_window='20'),
                    Excercise(description='комбо на пресс',
                              reps_window='по 20')
                ],
                rounds='2')
                ],
        actual_number=2,
        number=2),
Workout(description=" \n"
                    "вес примерно 85%+ от ПМ\n"
                    "последние 2 тяжелые, запас в 1-2 повторения",
        sets=[
            Set(description='по готовности',
                number=1,
                excersises=[
                    Excercise(description='подтягивания',
                              reps_window='3-5'),
                    Excercise(description='приседания со штангой на спине',
                              reps_window='3')
                    ],
                rounds='3'),
            Set(description='по готовности',
                number=2,
                excersises=[
                    Excercise(description='жим штанги лежа',
                              reps_window='3-5'),
                    Excercise(description='фронтальные приседания',
                              reps_window='3')
                ],
                rounds='3'),
            Set(description='с минимум отдыха',
                number=3,
                excersises=[
                    Excercise(description='тяга горизонтального блока',
                              reps_window='3-5'),
                    Excercise(description='обратная экстензия',
                              reps_window='20'),
                    Excercise(description="подъем гантелей на бицепс лежа "
                                          "под 45",
                              reps_window='8-10')
                ],
                rounds='2')
            ],
        actual_number=3,
        number=3)
    ],
    comment='')
]
