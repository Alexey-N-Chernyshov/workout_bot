"""
Telegram bot related code resides here.
"""

import telebot
import yaml
from controllers.controllers import Controllers
from data_model.data_model import DataModel
from data_model.users import UserAction
from google_sheets_feeder import google_sheets_adapter
from telebot.types import BotCommand


class TelegramBot:
    """
    Telegram bot class.
    """

    def __init__(self, token_filename):
        with open(token_filename, encoding="utf-8") as token_file:
            telegram_bot_token = token_file.readline().strip()
        self.bot = telebot.TeleBot(telegram_bot_token)

        self.data_model = DataModel(google_sheets_adapter)

        # init controllers
        self.controllers = Controllers(self.bot, self.data_model)

        self.start_handler = self.bot \
            .message_handler(commands=["start"])(self.handle_start)
        self.system_stats_handler = self.bot \
            .message_handler(
                                commands=["system_stats"]
                            )(self.handle_system_stats)
        self.message_handler = self.bot \
            .message_handler(content_types=["text"])(self.handle_message)

    def update_workout_tables(self):
        """
        Updates workout tables.
        """

        self.data_model.update_tables()

    def start_bot(self):
        """
        Starts telegram bot and enters infinity polling loop.
        """

        with open("secrets/config.yml", encoding="utf-8") as file:
            config = yaml.safe_load(file)
            table_id = config["spreadsheet_id"]
            pagenames = config["pagenames"]
            admins = config["admins"]
            users_storage = config["users_storage"]
            self.data_model.users.set_storage(users_storage)
            workout_table_ids_storage = config["workout_table_ids_storage"]
            self.data_model \
                .workout_table_names.set_storage(workout_table_ids_storage)
            self.data_model.workout_table_names.add_table(table_id, pagenames)
            for admin in admins:
                user_id = int(admin)
                self.data_model.users.get_or_create_user_context(user_id)
                self.data_model.users.set_administrative_permission(user_id)
                self.data_model.users.set_table_for_user(user_id, table_id)

        self.update_workout_tables()

        start_command = BotCommand("start", "Start using the bot")
        system_stats_command = BotCommand("system_stats",
                                          "Show system statistics")
        self.bot.set_my_commands([start_command, system_stats_command])

        self.bot.infinity_polling(none_stop=True, interval=1, timeout=30)

    def handle_start(self, message):
        """
        Handler for command /start that initializes a new user.
        """

        self.data_model.statistics.record_command()
        if message.chat.type != "private":
            self.bot.send_message(message.chat.id,
                                  "Бот доступен только в приватном чате.")
            return
        user_context = self.data_model \
            .users.get_or_create_user_context(message.from_user.id)
        user_context.user_id = message.from_user.id
        user_context.first_name = message.from_user.first_name
        user_context.last_name = message.from_user.last_name
        user_context.username = message.from_user.username
        user_context.chat_id = message.chat.id
        user_context.current_page = None
        user_context.current_week = None
        user_context.current_workout = None
        self.data_model.users.set_user_context(user_context)
        self.handle_message(message)

    def handle_system_stats(self, message):
        """
        Handler for command /system_stats shows statistics.
        """

        self.data_model.statistics.record_command()
        user_context = self.data_model \
            .users.get_user_context(message.from_user.id)

        text = 'Системная статистика:\n\n'
        time = self.data_model.statistics.get_training_plan_update_time()
        text += f"Расписание обновлено: {time:%Y-%m-%d %H:%M}\n"

        if user_context and user_context.administrative_permission:
            text += 'Количество запросов: '
            text += str(self.data_model.statistics.get_total_requests()) + "\n"
            text += 'Количество команд: '
            text += str(self.data_model.statistics.get_total_commands()) + "\n"
            text += 'Количество пользователей: '
            text += str(self.data_model.users.get_users_number()) + "\n"

        self.bot.send_message(message.chat.id, text)

    def handle_message(self, message):
        """
        Handles all text messages.
        """

        self.data_model.statistics.record_request()

        if self.controllers.authorization.handle_message(message):
            return

        user_context = \
            self.data_model.users.get_user_context(message.from_user.id)
        message_text = message.text.strip().lower()

        # change state actions
        if (user_context is not None
                and user_context.administrative_permission
                and user_context.action in (UserAction.TRAINING,
                                            UserAction.ADMINISTRATION)
                and message_text == "управление таблицами"):
            self.data_model \
                .users.set_user_action(user_context.user_id,
                                       UserAction.ADMIN_TABLE_MANAGEMENT)
            self.controllers.table_management \
                .show_table_management_panel(message.chat.id)
            return

        if (user_context is not None
                and user_context.administrative_permission
                and user_context.action in (UserAction.TRAINING,
                                            UserAction.ADMINISTRATION)
                and message_text == "управление пользователями"):
            self.data_model \
                .users.set_user_action(user_context.user_id,
                                       UserAction.ADMIN_USER_MANAGEMENT)
            self.controllers.user_management \
                .show_user_management_panel(message.chat.id)
            return

        if (user_context is not None
                and user_context.administrative_permission
                and user_context.action in (UserAction.ADMIN_USER_MANAGEMENT,
                                            UserAction.ADMIN_TABLE_MANAGEMENT,
                                            UserAction.TRAINING)
                and message_text == "администрирование"):
            self.data_model.users.set_user_action(user_context.user_id,
                                                  UserAction.ADMINISTRATION)
            self.controllers.administration \
                .show_admin_panel(message.chat.id, user_context)
            return

        if (user_context is not None
                and user_context.action in (UserAction.TRAINING,
                                            UserAction.ADMINISTRATION,
                                            UserAction.ADMIN_TABLE_MANAGEMENT)
                and message.text.strip().lower() == "перейти к тренировкам"):
            if (user_context.current_table_id is None
                    or user_context.current_page is None):
                self.data_model.users.set_user_action(user_context.user_id,
                                                      UserAction.CHOOSING_PLAN)
                self.controllers.training_management \
                    .change_plan_prompt(message.chat.id, user_context)
            else:
                self.data_model.users.set_user_action(user_context.user_id,
                                                      UserAction.TRAINING)
                self.controllers.training_management.send_workout(message.chat.id,
                                                      user_context)
            return

        if (self.controllers.administration.handle_message(message)
                or self.controllers.user_management.handle_message(message)
                or self.controllers.table_management.handle_message(message)
                or self.controllers
                    .training_management.handle_message(message)):
            return
