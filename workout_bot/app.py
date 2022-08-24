"""
Telegram bot for workouts app entry point.
"""

import time
import threading
from pathlib import Path
import schedule
import telebot
import yaml

from data_model.data_model import DataModel
from google_sheets_feeder import google_sheets_adapter
from telegram_bot.telegram_bot import TelegramBot

VERSION_FILE_NAME = 'git_commit_version.txt'
TELEGRAM_TOKEN_FILE = "secrets/telegram_token.txt"


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
        workout_table_ids_storage = config["workout_table_ids_storage"]

        data_model = DataModel(google_sheets_adapter, users_storage,
                               workout_table_ids_storage)
        data_model.workout_table_names.add_table(table_id, pagenames)
        for admin in admins:
            user_id = int(admin)
            data_model.users.get_or_create_user_context(user_id)
            data_model.users.set_administrative_permission(user_id)
            data_model.users.set_table_for_user(user_id, table_id)

        data_model.update_tables()

        return data_model

    return None


def scheduler(data_model):
    "Schedules google table updates daily at 3 a.m."

    schedule.every().day.at("03:00").do(data_model.update_tables)
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

    with open(TELEGRAM_TOKEN_FILE, encoding="utf-8") as token_file:
        telegram_bot_token = token_file.readline().strip()
    telebot = telebot.TeleBot(telegram_bot_token)

    app_data_model = init_data_model()

    bot = TelegramBot(telebot, app_data_model)

    scheduleThread = threading.Thread(target=scheduler, args=(app_data_model,))
    scheduleThread.daemon = True
    scheduleThread.start()

    bot.start_bot()
