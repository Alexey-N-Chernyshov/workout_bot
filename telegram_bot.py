import telebot
import google_sheets_adapter
import yaml
from workout_plan import WorkoutLibrary
from user import UserContext

telegram_bot_token_file = 'secrets/telegram_token.txt'
telegram_bot_token = ''
with open(telegram_bot_token_file) as f:
    telegram_bot_token = f.readline().strip()
bot = telebot.TeleBot(telegram_bot_token)

workout_library = WorkoutLibrary()
users = {}
# number of requests for statistics
total_requests = 0
total_commands = 0


def update_workout_library():
    global workout_library

    print('Updating workouts')
    config = yaml.safe_load(open("secrets/config.yml"))
    workout_library = google_sheets_adapter \
        .load_workouts(config['spreadsheet_id'], config['pagenames'])


def get_user_context(user_id):
    global users

    if user_id not in users:
        # default user plan
        user_plan = '2022 (гонка героев)'
        last_week = workout_library.get_week_number(user_plan) - 1
        users[user_id] = UserContext(user_plan, last_week, 0)
    return users[user_id]


def send_week_schedule(chat_id, user_context):
    text = workout_library.get_week_text_message(user_context.current_plan,
                                                 user_context.current_week)
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_next = telebot.types.KeyboardButton(text='Далее')
    keyboard.add(key_next)
    bot.send_message(chat_id, text, reply_markup=keyboard,
        parse_mode="MarkdownV2")


def send_workout(chat_id, user_context):
    text = workout_library.get_workout_text_message(user_context.current_plan,
        user_context.current_week,user_context.current_workout)
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_next = telebot.types.KeyboardButton(text='Далее')
    keyboard.add(key_next)
    bot.send_message(chat_id, text, reply_markup=keyboard,
        parse_mode="MarkdownV2")


def change_plan_prompt(chat_id):
    plans = workout_library.get_plan_names()
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    text = 'Выберите программу из списка:'
    for plan in plans:
        text += '\n - ' + plan
        button_text = 'Выбрать программу ' + plan
        button = telebot.types.KeyboardButton(text=button_text)
        keyboard.add(button)
    bot.send_message(chat_id, text, reply_markup=keyboard)


@bot.message_handler(commands=["start"])
def start(message):
    global total_commands
    total_commands += 1
    user_context = get_user_context(message.from_user.id)
    change_plan_prompt(message.chat.id)


@bot.message_handler(commands=["system_stats"])
def system_stats(message):
    global total_commands
    total_users = len(users)
    total_commands += 1
    text = 'Системная статистика:\n\n'
    text += 'Количество запросов: {}\n'.format(total_requests)
    text += 'Количество команд: {}\n'.format(total_commands)
    text += 'Количество пользователей: {}'.format(total_users)
    bot.send_message(message.chat.id, text)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global total_requests
    total_requests += 1
    user_context = get_user_context(message.from_user.id)

    if (message.text.strip().lower() == 'выбрать программу' \
            or message.text.strip().lower() == 'сменить программу' \
            or message.text.strip().lower() == 'поменять программу'):
        change_plan_prompt(message.chat.id)

    if (message.text.strip().lower().startswith('выбрать программу ')):
        plan = message.text.strip().lower()[18:]
        plans = workout_library.get_plan_names()
        if plan in plans:
            user_context.current_plan = plan
            user_context.current_week = workout_library.get_week_number(
                                            user_context.current_plan) - 1
            user_context.current_workout = 0
            bot.send_message(message.chat.id, 'Программа выбрана.')
            send_week_schedule(message.chat.id, user_context)
        else:
            bot.send_message(message.chat.id, 'Нет такой программы.')

    if message.text.strip().lower() == "далее":
        send_workout(message.chat.id, user_context)
        if user_context.current_workout < workout_library
                .get_workout_number(user_context.current_plan,
                                    user_context.current_week) - 1:
            user_context.current_workout += 1
        elif user_context.current_week < workout_library
                .get_week_number(user_context.current_plan) - 1:
            user_context.current_week += 1
            user_context.current_workout = 0
            send_week_schedule(message.chat.id, user_context)

    if message.text.strip().lower() == "первая неделя" \
            or message.text.strip().lower() == "начальная неделя":
        user_context.current_week = 0
        user_context.current_workout = 0
        send_week_schedule(message.chat.id, user_context)

    if message.text.strip().lower() == "последняя неделя" \
            or message.text.strip().lower() == "крайняя неделя" \
            or message.text.strip().lower() == "текущая неделя":
        user_context.current_week = workout_library
                .get_week_number(user_context.current_plan) - 1
        send_week_schedule(message.chat.id, user_context)
        user_context.current_workout = 0

    if message.text.strip().lower() == "следующая неделя":
        if user_context.current_week < workout_library
                .get_week_number(user_context.current_plan) - 1:
            user_context.current_week += 1
        send_week_schedule(message.chat.id, user_context)
        user_context.current_workout = 0

    if message.text.strip().lower() == "прошлая неделя" \
            or message.text.strip().lower() == "предыдущая неделя":
        if user_context.current_week > 0:
            user_context.current_week -= 1
        send_week_schedule(message.chat.id, user_context)
        user_context.current_workout = 0


def start_bot():
    update_workout_library()

    start = telebot.types.BotCommand("start", "Start using the bot")
    system_stats = telebot.types.BotCommand("system_stats",
                                            "Show system statistics")
    bot.set_my_commands([start, system_stats])

    bot.polling(none_stop=True, interval=1)
