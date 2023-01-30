"""
Test data
"""

# No Quality Assurance for the test data file.
# flake8: noqa

# Raw exercise data with empty lines and empty links.
RAW_EXERCISE_DATA = [
    ['подтягивания', 'https://youtu.be/J5CYP7MmEGg'],
    ['рывковая протяжка полная'],
    [],
    ['статика на шею лицом вверх',
     'https://www.youtube.com/watch?v=gI_4QqSIvEc'],
    [],
    ['гимнастика для плеч с палкой',
     'https://www.youtube.com/watch?v=x6ZiJrKs8x8'],
    ['пуловер', 'https://www.youtube.com/watch?v=hk8jSyUaNjU']
]

# Expected and sorted exercise links
EXPECTED_EXERCISE_DATA = {
    'гимнастика для плеч с палкой': 'https://www.youtube.com/watch?v=x6ZiJrKs8x8',
    'статика на шею лицом вверх': 'https://www.youtube.com/watch?v=gI_4QqSIvEc',
    'подтягивания': 'https://youtu.be/J5CYP7MmEGg',
    'пуловер': 'https://www.youtube.com/watch?v=hk8jSyUaNjU'
}
