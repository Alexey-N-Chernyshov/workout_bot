import telebot
import google_sheets_adapter
import yaml
from data_model.statistics import Statistics
from data_model.users import Users
from data_model.users import UserAction
from data_model.users import AddTableContext
from data_model.users import AddExcerciseLinkContext
from data_model.users import RemoveExcerciseLinkContext
from data_model.workout_plan import WorkoutLibrary
from data_model.workout_plan import excercise_links
from data_model.workout_plan import workout_tables
from telebot.types import KeyboardButton

telegram_bot_token_file = 'secrets/telegram_token.txt'
telegram_bot_token = ''
with open(telegram_bot_token_file) as f:
    telegram_bot_token = f.readline().strip()
bot = telebot.TeleBot(telegram_bot_token)

# data model
workout_library = WorkoutLibrary()
users = Users()
statistics = Statistics()

def update_workout_library():
    global workout_library
    global workout_tables

    google_sheets_adapter.load_workouts(workout_library, workout_tables)
    statistics.set_training_plan_update_time()


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


def show_admin_panel(chat_id, user_context):
    if user_context.administrative_permission:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                     one_time_keyboard=True)
        key_remove_table = KeyboardButton(text='Удалить таблицу')
        key_add_table = KeyboardButton(text='Добавить таблицу')
        keyboard.row(key_remove_table, key_add_table)
        key_reload_plans = KeyboardButton(text='Прочитать таблицы')
        keyboard.add(key_reload_plans)
        key_remove_workout_link = \
            KeyboardButton(text="Удалить ссылку на упражнение")
        key_add_workout_link = \
            KeyboardButton(text="Добавить ссылку на упражнение")
        keyboard.row(key_remove_workout_link, key_add_workout_link)
        key_training = KeyboardButton(text='Перейти к тренировкам')
        keyboard.add(key_training)
        bot.send_message(chat_id, "Администрирование", reply_markup=keyboard,
                         parse_mode="MarkdownV2")

def add_pages_prompt(chat_id, user_context):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                 one_time_keyboard=True)
    key_done = KeyboardButton(text='Готово')
    keyboard.add(key_done)
    bot.send_message(chat_id,
                     "Введите название страницы или нажмите \"Готово\"",
                     reply_markup=keyboard,
                     parse_mode="MarkdownV2")


def remove_excercise_link_prompt(chat_id, user_context):
    global excercise_links
    name = user_context.user_input_data.name
    link = excercise_links[name]
    text = "Удалить упражнение?\n\n[{}]({})".format(name, link)
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_no = KeyboardButton(text="Нет")
    key_yes = KeyboardButton(text="Да")
    keyboard.row(key_no, key_yes)
    bot.send_message(chat_id, text, disable_web_page_preview=True,
                     reply_markup=keyboard, parse_mode="MarkdownV2")

def add_excercise_link_prompt(chat_id, user_context):
    name = user_context.user_input_data.name
    link = user_context.user_input_data.link
    text = "Добавить упражнение?\n\n[{}]({})".format(name, link)
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_no = KeyboardButton(text="Нет")
    key_yes = KeyboardButton(text="Да")
    keyboard.row(key_no, key_yes)
    bot.send_message(chat_id, text, disable_web_page_preview=True,
                     reply_markup=keyboard, parse_mode="MarkdownV2")

def change_plan_prompt(chat_id, user_context):
    """
    Asks the user with user_id to choose plan.
    """

    plans = workout_library.get_plan_names()
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

    plans = workout_library.get_plan_names()
    if plan in plans:
        (table_name, page_name) = plan.split(" - ")
        user_context.current_table_id = \
            workout_library.get_table_id_by_name(table_name)
        user_context.current_page = page_name
        user_context.current_week = workout_library.get_week_number(
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
    message = \
        workout_library.get_week_text_message(user_context.current_table_id,
                                              user_context.current_page,
                                              user_context.current_week)
    send_with_next_or_all_buttons(chat_id, user_context, message)


def send_workout(chat_id, user_context):
    message = \
        workout_library.get_workout_text_message(user_context.current_table_id,
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
    global statistics
    statistics.record_command()
    if message.chat.type != "private":
        bot.send_message(message.chat.id,
                         "Бот доступен только в приватном чате.")
        return
    user_context = users.get_user_context(message.from_user.id)
    user_context.current_table_id = None
    user_context.current_page = None
    user_context.current_week = None
    user_context.current_workout = None
    if user_context.administrative_permission:
        user_context.action = UserAction.administration
        show_admin_panel(message.chat.id, user_context)
    else:
        user_context.action = UserAction.choosing_plan
        change_plan_prompt(message.chat.id, user_context)

@bot.message_handler(commands=["system_stats"])
def system_stats(message):
    global statistics
    statistics.record_command()
    user_context = users.get_user_context(message.from_user.id)

    text = 'Системная статистика:\n\n'
    text += \
        "Расписание обновлено: {:%Y-%m-%d %H:%M}\n" \
        .format(statistics.get_training_plan_update_time())

    if user_context.administrative_permission:
        text += 'Количество запросов: {}\n'.format(statistics.get_total_requests())
        text += 'Количество команд: {}\n'.format(statistics.get_total_commands())
        text += 'Количество пользователей: {}'.format(users.get_unique_users())

    bot.send_message(message.chat.id, text)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global workout_tables
    global excercise_links
    global statistics
    statistics.record_request()
    user_context = users.get_user_context(message.from_user.id)

    # waiting for specific input
    if user_context.action == UserAction.choosing_plan:
        plan = message.text.strip()
        change_plan(message.chat.id, user_context, message.text.strip())
        return

    if user_context.action == UserAction.admin_adding_table:
        user_context.user_input_data.table_id = message.text
        user_context.action = UserAction.admin_adding_pages
        add_pages_prompt(message.chat.id, user_context)
        user_context.action = UserAction.admin_adding_pages
        return

    if user_context.action == UserAction.admin_adding_pages:
        if message.text.strip().lower() == "готово":
            workout_tables[user_context.user_input_data.table_id] = \
                user_context.user_input_data.pages
            user_context.action = UserAction.administration
            user_context.user_input_data = None
            show_admin_panel(message.chat.id, user_context)
        else:
            user_context.user_input_data.pages.append(message.text)
            add_pages_prompt(message.chat.id, user_context)
        return

    if user_context.action == UserAction.admin_removing_excercise_name:
        name = message.text.strip().lower()
        if name in excercise_links:
            user_context.user_input_data.name = name
            remove_excercise_link_prompt(message.chat.id, user_context)
            user_context.action = UserAction.admin_removing_excercise_prove
        else:
            bot.send_message(message.chat.id, "Нет такого упражнения")
            user_context.action = UserAction.administration
            show_admin_panel(message.chat.id, user_context)
        return

    if user_context.action == UserAction.admin_removing_excercise_prove:
        input = message.text.strip().lower()
        if input == "да":
            del excercise_links[user_context.user_input_data.name]
            user_context.action = UserAction.administration
            user_context.user_input_data = None
            show_admin_panel(message.chat.id, user_context)
        elif input == "нет":
            user_context.action = UserAction.administration
            user_context.user_input_data = None
            show_admin_panel(message.chat.id, user_context)
        else:
            remove_excercise_link_prompt(message.chat.id, user_context)
        return

    if user_context.action == UserAction.admin_adding_excercise_name:
        user_context.user_input_data.name = message.text.strip().lower()
        bot.send_message(message.chat.id, "Введите ссылку")
        user_context.action = UserAction.admin_adding_excercise_link
        return

    if user_context.action == UserAction.admin_adding_excercise_link:
        user_context.user_input_data.link = message.text.strip()
        add_excercise_link_prompt(message.chat.id, user_context)
        user_context.action = UserAction.admin_adding_excercise_prove
        return

    if user_context.action == UserAction.admin_adding_excercise_prove:
        input = message.text.strip().lower()
        if input == "да":
            excercise_links[user_context.user_input_data.name] = \
                user_context.user_input_data.link
            user_context.action = UserAction.administration
            user_context.user_input_data = None
            show_admin_panel(message.chat.id, user_context)
        elif input == "нет":
            user_context.action = UserAction.administration
            user_context.user_input_data = None
            show_admin_panel(message.chat.id, user_context)
        else:
            add_excercise_link_prompt(message.chat.id, user_context)
        return

    # change user action commands
    if message.text.strip().lower() == "перейти к тренировкам":
        if (user_context.current_table_id == None
            or user_context.current_page == None):
            user_context.action = UserAction.choosing_plan
            change_plan_prompt(message.chat.id, user_context)
        else:
            user_context.action = UserAction.training
            send_workout(message.chat.id, user_context)
        return

    if message.text.strip().lower() == "администрирование":
        user_context.action = UserAction.administration
        show_admin_panel(message.chat.id, user_context)
        return

    if (message.text.strip().lower() == "добавить таблицу"
        and user_context.administrative_permission):
        user_context.action = UserAction.admin_adding_table
        user_context.user_input_data = AddTableContext()
        text = "Введите идентификатор таблицы.\n\n" + \
            "Идентификатор может быть найден в ссылке на таблицу (spreadsheetId):\n" + \
            "<code>https://docs.google.com/spreadsheets/d/</code><b><u>spreadsheetId</u></b><code>/edit#gid=0</code>"
        bot.send_message(message.chat.id, text, parse_mode="HTML")
        return

    if (message.text.strip().lower() == "удалить ссылку на упражнение"
            and user_context.administrative_permission):
        user_context.action = UserAction.admin_removing_excercise_name
        user_context.user_input_data = RemoveExcerciseLinkContext()
        bot.send_message(message.chat.id, "Введите название упражнения")
        return

    if (message.text.strip().lower() == "добавить ссылку на упражнение"
            and user_context.administrative_permission):
        user_context.action = UserAction.admin_adding_excercise_name
        user_context.user_input_data = AddExcerciseLinkContext()
        bot.send_message(message.chat.id, "Введите название упражнения")
        return

    # actions
    if message.text.strip().lower() == "прочитать таблицы":
        if user_context.administrative_permission:
            update_workout_library()
            bot.send_message(message.chat.id, "Таблицы обновлены.")
            show_admin_panel(message.chat.id, user_context)
        return

    if (user_context.current_table_id == None
        or user_context.current_page == None):
        user_context.action = UserAction.choosing_plan
    if (message.text.strip().lower() == "выбрать программу"
            or message.text.strip().lower() == "сменить программу"
            or message.text.strip().lower() == "поменять программу"):
        user_context.action = UserAction.choosing_plan
        change_plan_prompt(message.chat.id, user_context)

    if (message.text.strip().lower() == "далее"
            or message.text.strip().lower() == "следующая тренировка"):
        if user_context.current_workout < workout_library \
                .get_workout_number(user_context.current_table_id,
                                    user_context.current_page,
                                    user_context.current_week) - 1:
            user_context.current_workout += 1
        elif user_context.current_week < workout_library \
                .get_week_number(user_context.current_table_id,
                                 user_context.current_page) - 1:
            user_context.current_week += 1
            user_context.current_workout = 0
            send_week_schedule(message.chat.id, user_context)
        send_workout(message.chat.id, user_context)
        return

    if message.text.strip().lower() == "все действия":
        send_all_actions(message.chat.id, user_context)
        return

    if (message.text.strip().lower() == "первая неделя"
            or message.text.strip().lower() == "начальная неделя"):
        user_context.current_week = 0
        user_context.current_workout = 0
        send_week_schedule(message.chat.id, user_context)
        send_workout(message.chat.id, user_context)
        return

    if (message.text.strip().lower() == "последняя неделя"
            or message.text.strip().lower() == "крайняя неделя"
            or message.text.strip().lower() == "текущая неделя"):
        user_context.current_week = workout_library \
            .get_week_number(user_context.current_table_id,
                             user_context.current_page) - 1
        user_context.current_workout = 0
        send_week_schedule(message.chat.id, user_context)
        send_workout(message.chat.id, user_context)
        return

    if message.text.strip().lower() == "следующая неделя":
        if user_context.current_week < workout_library \
                .get_week_number(user_context.current_table_id,
                                 user_context.current_page) - 1:
            user_context.current_week += 1
        user_context.current_workout = 0
        send_week_schedule(message.chat.id, user_context)
        send_workout(message.chat.id, user_context)
        return

    if (message.text.strip().lower() == "прошлая неделя"
            or message.text.strip().lower() == "предыдущая неделя"):
        if user_context.current_week > 0:
            user_context.current_week -= 1
        user_context.current_workout = 0
        send_week_schedule(message.chat.id, user_context)
        send_workout(message.chat.id, user_context)
        return

def start_bot():
    global workout_tables
    global users

    config = yaml.safe_load(open("secrets/config.yml"))
    table_id = config['spreadsheet_id']
    pagenames = config['pagenames']
    workout_tables[table_id] = pagenames

    users.set_administrative_permission(96539438)

    update_workout_library()

    start = telebot.types.BotCommand("start", "Start using the bot")
    system_stats = telebot.types.BotCommand("system_stats",
                                            "Show system statistics")
    bot.set_my_commands([start, system_stats])

    bot.polling(none_stop=True, interval=1)
