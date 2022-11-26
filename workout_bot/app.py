"""
Telegram bot for workouts app entry point.
"""

import logging
import time
import threading
from pathlib import Path
import schedule
import yaml

from data_model.data_model import DataModel
from telegram_bot.telegram_bot import TelegramBot
from telegram.ext import ApplicationBuilder
from google_sheets_feeder.google_sheets_loader import GoogleSheetsLoader

VERSION_FILE_NAME = 'git_commit_version.txt'
TELEGRAM_TOKEN_FILE = "secrets/telegram_token.txt"


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def init_data_model():
    """
    Initializes data model.
    """

    with open("secrets/config.yml", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
        table_id = config["spreadsheet_id"]
        pagenames = config["pagenames"]
        admins = config["admins"]
        users_storage = config["users_storage"]
        exercise_links_table_id = config["exercise_links_table_id"]
        exercise_links_pagename = config["exercise_links_pagename"]
        workout_table_ids_storage = config["workout_table_ids_storage"]

        data_model = DataModel(users_storage,
                               exercise_links_table_id,
                               exercise_links_pagename,
                               workout_table_ids_storage)
        data_model.workout_table_names.add_table(table_id, pagenames)
        for admin in admins:
            user_id = int(admin)
            data_model.users.get_or_create_user_context(user_id)
            data_model.users.set_administrative_permission(user_id)
            data_model.users.set_table_for_user(user_id, table_id)

        data_model.update_tables()

        return data_model


def scheduler(data_model):
    "Schedules google table updates daily at 3 a.m."

    schedule.every().day.at("03:00").do(data_model.update_tables)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    # print version
    version_file = Path(VERSION_FILE_NAME)
    if version_file.is_file():
        with open(VERSION_FILE_NAME, encoding="utf-8") as file:
            version = file.readline().strip()
            logging.info("workout_bot %s", version)

    with open(TELEGRAM_TOKEN_FILE, encoding="utf-8") as token_file:
        telegram_bot_token = token_file.readline().strip()
    telegram_application = ApplicationBuilder() \
        .token(telegram_bot_token).build()

    app_data_model = init_data_model()

    bot = TelegramBot(telegram_application,
                      GoogleSheetsLoader(),
                      app_data_model)

    scheduleThread = threading.Thread(target=scheduler, args=(app_data_model,))
    scheduleThread.daemon = True
    scheduleThread.start()

    bot.start_bot()
