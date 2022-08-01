"""
Telegram bot related code resides here.
"""

import telebot
import yaml
from controllers.administration import Administration
from controllers.authorization import Authorization
from controllers.table_management import TableManagement
from controllers.user_management import UserManagement
from controllers.training_management import TrainingManagement
from data_model.data_model import DataModel
from data_model.users import UserAction
from google_sheets_feeder import google_sheets_adapter


telegram_bot_token_file = 'secrets/telegram_token.txt'
telegram_bot_token = ''
with open(telegram_bot_token_file) as f:
    telegram_bot_token = f.readline().strip()
bot = telebot.TeleBot(telegram_bot_token)

# data model
data_model = DataModel(google_sheets_adapter)

administration = Administration(bot, data_model)
authorization = Authorization(bot, data_model)
user_management = UserManagement(bot, data_model)
table_management = TableManagement(bot, data_model)
training_management = TrainingManagement(bot, data_model)


def update_workout_tables():
    """
    Updates workout tables.
    """

    data_model.update_tables()


@bot.message_handler(commands=["start"])
def start(message):
    """
    Handler for command /start that initializes a new user.
    """

    data_model.statistics.record_command()
    if message.chat.type != "private":
        bot.send_message(message.chat.id,
                         "Бот доступен только в приватном чате.")
        return
    user_context = \
        data_model.users.get_or_create_user_context(message.from_user.id)
    user_context.user_id = message.from_user.id
    user_context.first_name = message.from_user.first_name
    user_context.last_name = message.from_user.last_name
    user_context.username = message.from_user.username
    user_context.chat_id = message.chat.id
    user_context.current_page = None
    user_context.current_week = None
    user_context.current_workout = None
    data_model.users.set_user_context(user_context)
    get_text_messages(message)


@bot.message_handler(commands=["system_stats"])
def system_stats(message):
    """
    Handler for command /system_stats shows statistics.
    """

    data_model.statistics.record_command()
    user_context = data_model.users.get_user_context(message.from_user.id)

    text = 'Системная статистика:\n\n'
    text += \
        "Расписание обновлено: {:%Y-%m-%d %H:%M}\n" \
        .format(data_model.statistics.get_training_plan_update_time())

    if user_context and user_context.administrative_permission:
        text += 'Количество запросов: '
        text += str(data_model.statistics.get_total_requests()) + "\n"
        text += 'Количество команд: '
        text += str(data_model.statistics.get_total_commands()) + "\n"
        text += 'Количество пользователей: '
        text += str(data_model.users.get_users_number()) + "\n"

    bot.send_message(message.chat.id, text)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    """
    Handles all text messages.
    """

    data_model.statistics.record_request()

    if authorization.handle_message(message):
        return

    user_context = \
        data_model.users.get_user_context(message.from_user.id)
    message_text = message.text.strip().lower()

    # change state actions
    if (user_context is not None
            and user_context.administrative_permission
            and user_context.action in (UserAction.TRAINING,
                                        UserAction.ADMINISTRATION)
            and message_text == "управление таблицами"):
        data_model.users.set_user_action(user_context.user_id,
                                         UserAction.ADMIN_TABLE_MANAGEMENT)
        table_management.show_table_management_panel(message.chat.id)
        return

    if (user_context is not None
            and user_context.administrative_permission
            and user_context.action in (UserAction.TRAINING,
                                        UserAction.ADMINISTRATION)
            and message_text == "управление пользователями"):
        data_model.users.set_user_action(user_context.user_id,
                                         UserAction.ADMIN_USER_MANAGEMENT)
        user_management.show_user_management_panel(message.chat.id)
        return

    if (user_context is not None
            and user_context.administrative_permission
            and user_context.action in (UserAction.ADMIN_USER_MANAGEMENT,
                                        UserAction.ADMIN_TABLE_MANAGEMENT,
                                        UserAction.TRAINING)
            and message_text == "администрирование"):
        data_model.users.set_user_action(user_context.user_id,
                                         UserAction.ADMINISTRATION)
        administration.show_admin_panel(message.chat.id, user_context)
        return

    if (user_context is not None
            and user_context.action in (UserAction.TRAINING,
                                        UserAction.ADMINISTRATION,
                                        UserAction.ADMIN_TABLE_MANAGEMENT)
            and message.text.strip().lower() == "перейти к тренировкам"):
        if (user_context.current_table_id is None
                or user_context.current_page is None):
            data_model.users.set_user_action(user_context.user_id,
                                             UserAction.CHOOSING_PLAN)
            training_management.change_plan_prompt(message.chat.id,
                                                   user_context)
        else:
            data_model.users.set_user_action(user_context.user_id,
                                             UserAction.TRAINING)
            training_management.send_workout(message.chat.id, user_context)
        return

    if administration.handle_message(message):
        return

    if user_management.handle_message(message):
        return

    if table_management.handle_message(message):
        return

    if training_management.handle_message(message):
        return


def start_bot():
    """
    Starts telegram bot and enters infinity polling loop.
    """

    with open("secrets/config.yml", encoding="utf-8") as file:
        config = yaml.safe_load(file)
        table_id = config["spreadsheet_id"]
        pagenames = config["pagenames"]
        admins = config["admins"]
        users_storage = config["users_storage"]
        data_model.users.set_storage(users_storage)
        workout_table_ids_storage = config["workout_table_ids_storage"]
        data_model.workout_table_names.set_storage(workout_table_ids_storage)
        data_model.workout_table_names.add_table(table_id, pagenames)
        for admin in admins:
            user_id = int(admin)
            data_model.users.get_or_create_user_context(user_id)
            data_model.users.set_administrative_permission(user_id)
            data_model.users.set_table_for_user(user_id, table_id)

    update_workout_tables()

    start_command = telebot.types.BotCommand("start", "Start using the bot")
    system_stats_command = telebot.types.BotCommand("system_stats",
                                                    "Show system statistics")
    bot.set_my_commands([start_command, system_stats_command])

    bot.infinity_polling(none_stop=True, interval=1, timeout=30)
