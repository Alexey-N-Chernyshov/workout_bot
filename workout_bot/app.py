"""
Telegram bot for workouts app entry point.
"""

import time
import threading
from pathlib import Path
import schedule

from telegram_bot.telegram_bot import TelegramBot

VERSION_FILE_NAME = 'git_commit_version.txt'
TELEGRAM_TOKEN_FILE = "secrets/telegram_token.txt"


def scheduler(telegram_bot):
    "Schedules google table updates daily at 3 a.m."

    schedule.every().day.at("03:00").do(telegram_bot.update_workout_tables)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    # print version
    version_file = Path(VERSION_FILE_NAME)
    if version_file.is_file():
        with open(VERSION_FILE_NAME, encoding="utf-8") as file:
            version = file.readline().strip()
            print("workout_bot " + version)

    bot = TelegramBot(TELEGRAM_TOKEN_FILE)

    scheduleThread = threading.Thread(target=scheduler, args=(bot,))
    scheduleThread.daemon = True
    scheduleThread.start()

    bot.start_bot()
