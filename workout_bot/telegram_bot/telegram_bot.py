import telebot
import yaml
from controllers.administration import Administration
from controllers.authorization import Authorization
from controllers.table_management import TableManagement
from controllers.user_management import UserManagement
from data_model.data_model import DataModel
from data_model.users import UserAction
from google_sheets_feeder import google_sheets_adapter
from view.workouts import get_workout_text_message
from view.workouts import get_week_routine_text_message


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


def update_workout_tables():
    global data_model
    data_model.update_tables()


def send_with_next_or_all_buttons(chat_id, user_context, message):
    """
    Sends message and adds buttons "Далее", "Все действия"
    """

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_all = telebot.types.KeyboardButton(text='Все действия')
    key_next = telebot.types.KeyboardButton(text='Далее')
    keyboard.row(key_all, key_next)

    if user_context.administrative_permission:
        key_admin = telebot.types.KeyboardButton(text='Администрирование')
        keyboard.add(key_admin)

    bot.send_message(chat_id, message, disable_web_page_preview=True,
                     reply_markup=keyboard, parse_mode="MarkdownV2")


def change_plan_prompt(chat_id, user_context):
    """
    Asks the user with user_id to choose plan.
    """

    table_id = user_context.current_table_id
    if (not table_id
            or not data_model.workout_plans.is_table_id_present(table_id)):
        bot.send_message(chat_id, "Вам не назначена программа тренировок")
        if user_context.administrative_permission:
            data_model.users.set_user_action(user_context.user_id,
                                             UserAction.administration)
            administration.show_admin_panel(chat_id, user_context)
        return

    plans = data_model.workout_plans.get_plan_names(table_id)
    if plans:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        text = 'Выберите программу из списка:'
        for plan in plans:
            text += '\n - ' + plan
            button = telebot.types.KeyboardButton(text=plan)
            keyboard.add(button)
        bot.send_message(chat_id, text, reply_markup=keyboard)
    else:
        bot.send_message(chat_id, "Для вас ещё нет программы тренировок.")


def change_plan(chat_id, user_context, plan):
    """
    Changes plan to the selected one for user.
    """

    plans = (
        data_model.
        workout_plans.get_plan_names(user_context.current_table_id)
    )
    if plan in plans:
        user_context.current_page = plan
        user_context.current_week = data_model.workout_plans.get_week_number(
            user_context.current_table_id, user_context.current_page) - 1
        user_context.current_workout = 0
        user_context.action = UserAction.training
        bot.send_message(chat_id, 'Программа выбрана.')
        send_week_schedule(chat_id, user_context)
        send_workout(chat_id, user_context)
    else:
        bot.send_message(chat_id, 'Нет такой программы.')
        change_plan_prompt(chat_id, user_context)


def send_week_schedule(chat_id, user_context):
    message = get_week_routine_text_message(data_model,
                                            user_context.current_table_id,
                                            user_context.current_page,
                                            user_context.current_week)
    send_with_next_or_all_buttons(chat_id, user_context, message)


def send_workout(chat_id, user_context):
    message = get_workout_text_message(data_model,
                                       user_context.current_table_id,
                                       user_context.current_page,
                                       user_context.current_week,
                                       user_context.current_workout)
    send_with_next_or_all_buttons(chat_id, user_context, message)


def send_all_actions(chat_id, user_context):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_change_plan = telebot.types.KeyboardButton(text='Сменить программу')
    keyboard.add(key_change_plan)
    key_first_week = telebot.types.KeyboardButton(text='Начальная неделя')
    key_last_week = telebot.types.KeyboardButton(text='Последняя неделя')
    keyboard.row(key_first_week, key_last_week)
    key_previous_week = telebot.types.KeyboardButton(text='Прошлая неделя')
    key_next_week = telebot.types.KeyboardButton(text='Следующая неделя')
    keyboard.row(key_previous_week, key_next_week)
    key_next = telebot.types.KeyboardButton(text='Следующая тренировка')
    keyboard.add(key_next)
    key_training = telebot.types.KeyboardButton(text='Перейти к тренировкам')
    keyboard.add(key_training)
    bot.send_message(chat_id, "Доступные действия:", reply_markup=keyboard,
                     parse_mode="MarkdownV2")


@bot.message_handler(commands=["start"])
def start(message):
    global data_model
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
    get_text_messages(message)


@bot.message_handler(commands=["system_stats"])
def system_stats(message):
    global data_model
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
    global data_model

    data_model.statistics.record_request()

    if authorization.handle_message(message):
        return

    user_context = \
        data_model.users.get_user_context(message.from_user.id)
    message_text = message.text.strip().lower()

    # change state actions
    if (user_context is not None
            and user_context.administrative_permission
            and (user_context.action == UserAction.training
                 or user_context.action == UserAction.administration)
            and message_text == "управление таблицами"):
        user_context.action = UserAction.admin_table_management
        table_management.show_table_management_panel(message.chat.id,
                                                     user_context)
        return

    if (user_context is not None
            and user_context.administrative_permission
            and (user_context.action == UserAction.training
                 or user_context.action == UserAction.administration)
            and message_text == "управление пользователями"):
        user_context.action = UserAction.admin_user_management
        user_management.show_user_management_panel(message.chat.id)
        return

    if (user_context is not None
            and user_context.administrative_permission
            and (user_context.action == UserAction.admin_user_management
                 or user_context.action == UserAction.admin_table_management
                 or user_context.action == UserAction.training)
            and message_text == "администрирование"):
        user_context.action = UserAction.administration
        administration.show_admin_panel(message.chat.id, user_context)
        return

    if (user_context is not None
            and (user_context.action == UserAction.training
                 or user_context.action == UserAction.administration
                 or user_context.action == UserAction.admin_table_management)
            and message.text.strip().lower() == "перейти к тренировкам"):
        if (user_context.current_table_id is None
                or user_context.current_page is None):
            user_context.action = UserAction.choosing_plan
            change_plan_prompt(message.chat.id, user_context)
        else:
            user_context.action = UserAction.training
            send_workout(message.chat.id, user_context)
        return

    if administration.handle_message(message):
        return

    if user_management.handle_message(message):
        return

    if table_management.handle_message(message):
        return

    # actions
    if user_context.action == UserAction.choosing_plan:
        change_plan(message.chat.id, user_context, message.text.strip())
        return

    if user_context.action == UserAction.training:
        if (user_context.current_table_id is None
                or user_context.current_page is None):
            user_context.action = UserAction.choosing_plan
        if (message_text == "выбрать программу"
                or message_text == "сменить программу"
                or message_text == "поменять программу"):
            user_context.action = UserAction.choosing_plan
            change_plan_prompt(message.chat.id, user_context)

        if (message_text == "далее" or message_text == "следующая тренировка"):
            if user_context.current_workout < data_model.workout_plans \
                    .get_workout_number(user_context.current_table_id,
                                        user_context.current_page,
                                        user_context.current_week) - 1:
                user_context.current_workout += 1
            elif user_context.current_week < data_model.workout_plans \
                    .get_week_number(user_context.current_table_id,
                                     user_context.current_page) - 1:
                user_context.current_week += 1
                user_context.current_workout = 0
                send_week_schedule(message.chat.id, user_context)
            send_workout(message.chat.id, user_context)
            return

        if message_text == "все действия":
            send_all_actions(message.chat.id, user_context)
            return

        if (message_text == "первая неделя"
                or message_text == "начальная неделя"):
            user_context.current_week = 0
            user_context.current_workout = 0
            send_week_schedule(message.chat.id, user_context)
            send_workout(message.chat.id, user_context)
            return

        if (message_text == "последняя неделя"
                or message_text == "крайняя неделя"
                or message_text == "текущая неделя"):
            user_context.current_week = data_model.workout_plans \
                .get_week_number(user_context.current_table_id,
                                 user_context.current_page) - 1
            user_context.current_workout = 0
            send_week_schedule(message.chat.id, user_context)
            send_workout(message.chat.id, user_context)
            return

        if message_text == "следующая неделя":
            if user_context.current_week < data_model.workout_plans \
                    .get_week_number(user_context.current_table_id,
                                     user_context.current_page) - 1:
                user_context.current_week += 1
            user_context.current_workout = 0
            send_week_schedule(message.chat.id, user_context)
            send_workout(message.chat.id, user_context)
            return

        if (message_text == "прошлая неделя"
                or message_text == "предыдущая неделя"):
            if user_context.current_week > 0:
                user_context.current_week -= 1
            user_context.current_workout = 0
            send_week_schedule(message.chat.id, user_context)
            send_workout(message.chat.id, user_context)
            return


def start_bot():
    global data_model

    config = yaml.safe_load(open("secrets/config.yml"))
    table_id = config["spreadsheet_id"]
    pagenames = config["pagenames"]
    admins = config["admins"]
    workout_table_ids_storage = config["workout_table_ids_storage"]
    data_model.workout_table_names.set_storage(workout_table_ids_storage)
    data_model.workout_table_names.add_table(table_id, pagenames)
    for admin in admins:
        user_id = int(admin)
        data_model.users.get_or_create_user_context(user_id)
        data_model.users.set_administrative_permission(user_id)
        data_model.users.set_table_for_user(user_id, table_id)

    update_workout_tables()

    start = telebot.types.BotCommand("start", "Start using the bot")
    system_stats = telebot.types.BotCommand("system_stats",
                                            "Show system statistics")
    bot.set_my_commands([start, system_stats])

    bot.infinity_polling(none_stop=True, interval=1, timeout=30)
