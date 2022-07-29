"""
Telegram bot for workouts app entry point.
"""

import time
import threading
from pathlib import Path
import schedule

from telegram_bot import telegram_bot

VERSION_FILE_NAME = 'git_commit_version.txt'


def scheduler():
    "Schedules google table updates daily at 3 a.m."

    schedule.every().day.at("03:00").do(telegram_bot.update_workout_library)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    # print version
    config_file = Path(VERSION_FILE_NAME)
    if config_file.is_file():
        with open(VERSION_FILE_NAME, encoding="utf-8") as f:
            version = f.readline().strip()
            print('workout_bot ' + version)

    scheduleThread = threading.Thread(target=scheduler)
    scheduleThread.daemon = True
    scheduleThread.start()

    telegram_bot.start_bot()
