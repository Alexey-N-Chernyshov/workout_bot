import telebot
import yaml
from controllers.table_management import TableManagement
from data_model.data_model import DataModel
from data_model.users import UserAction
from data_model.users import AddExcerciseLinkContext
from data_model.users import RemoveExcerciseLinkContext
from data_model.workout_plan import WorkoutLibrary
from data_model.workout_plan import excercise_links
from google_sheets_feeder import google_sheets_adapter
from telebot.types import KeyboardButton

telegram_bot_token_file = 'secrets/telegram_token.txt'
telegram_bot_token = ''
with open(telegram_bot_token_file) as f:
    telegram_bot_token = f.readline().strip()
bot = telebot.TeleBot(telegram_bot_token)

# data model
data_model = DataModel(google_sheets_adapter)

table_management = TableManagement(bot, data_model)

def update_workout_library():
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

def show_admin_panel(chat_id, user_context):
    if user_context.administrative_permission:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                     one_time_keyboard=True)
        key_table_management = KeyboardButton(text='Управление таблицами')
        keyboard.add(key_table_management)
        key_remove_workout_link = \
            KeyboardButton(text="Удалить ссылку на упражнение")
        key_add_workout_link = \
            KeyboardButton(text="Добавить ссылку на упражнение")
        keyboard.row(key_remove_workout_link, key_add_workout_link)
        key_training = KeyboardButton(text='Перейти к тренировкам')
        keyboard.add(key_training)
        bot.send_message(chat_id, "Администрирование", reply_markup=keyboard,
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

    plans = data_model.workout_library.get_plan_names()
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

    plans = data_model.workout_library.get_plan_names()
    if plan in plans:
        (table_name, page_name) = plan.split(" - ")
        user_context.current_table_id = \
            data_model.workout_library.get_table_id_by_name(table_name)
        user_context.current_page = page_name
        user_context.current_week = data_model.workout_library.get_week_number(
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
        data_model.workout_library.get_week_text_message(user_context.current_table_id,
                                              user_context.current_page,
                                              user_context.current_week)
    send_with_next_or_all_buttons(chat_id, user_context, message)


def send_workout(chat_id, user_context):
    message = \
        data_model.workout_library.get_workout_text_message(user_context.current_table_id,
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
    user_context = data_model.users.get_user_context(message.from_user.id)
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
    global data_model
    data_model.statistics.record_command()
    user_context = data_model.users.get_user_context(message.from_user.id)

    text = 'Системная статистика:\n\n'
    text += \
        "Расписание обновлено: {:%Y-%m-%d %H:%M}\n" \
        .format(data_model.statistics.get_training_plan_update_time())

    if user_context.administrative_permission:
        text += 'Количество запросов: {}\n'.format(data_model.statistics.get_total_requests())
        text += 'Количество команд: {}\n'.format(data_model.statistics.get_total_commands())
        text += 'Количество пользователей: {}'.format(data_model.users.get_unique_users())

    bot.send_message(message.chat.id, text)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global data_model

    data_model.statistics.record_request()
    user_context = data_model.users.get_user_context(message.from_user.id)

    # waiting for specific input
    if user_context.action == UserAction.choosing_plan:
        plan = message.text.strip()
        change_plan(message.chat.id, user_context, message.text.strip())
        return

    if table_management.handle_message(message):
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

    if (message.text.strip().lower() == "администрирование"
        and user_context.administrative_permission):
        user_context.action = UserAction.administration
        show_admin_panel(message.chat.id, user_context)
        return

    if (message.text.strip().lower() == "управление таблицами"
        and user_context.administrative_permission):
        user_context.action = UserAction.admin_table_management
        table_management.show_table_management_panel(message.chat.id,
                                                     user_context)
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
        if user_context.current_workout < data_model.workout_library \
                .get_workout_number(user_context.current_table_id,
                                    user_context.current_page,
                                    user_context.current_week) - 1:
            user_context.current_workout += 1
        elif user_context.current_week < data_model.workout_library \
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
        user_context.current_week = data_model.workout_library \
            .get_week_number(user_context.current_table_id,
                             user_context.current_page) - 1
        user_context.current_workout = 0
        send_week_schedule(message.chat.id, user_context)
        send_workout(message.chat.id, user_context)
        return

    if message.text.strip().lower() == "следующая неделя":
        if user_context.current_week < data_model.workout_library \
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
    global data_model

    config = yaml.safe_load(open("secrets/config.yml"))
    table_id = config['spreadsheet_id']
    pagenames = config['pagenames']
    data_model.add_table(table_id, pagenames)

    data_model.users.set_administrative_permission(96539438)

    update_workout_library()

    start = telebot.types.BotCommand("start", "Start using the bot")
    system_stats = telebot.types.BotCommand("system_stats",
                                            "Show system statistics")
    bot.set_my_commands([start, system_stats])

    bot.polling(none_stop=True, interval=1)
