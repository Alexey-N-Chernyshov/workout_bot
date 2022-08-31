"""
Provides user interaction for training.
"""

from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from data_model.users import UserAction
from view.workouts import get_workout_text_message
from view.workouts import get_week_routine_text_message


async def start_training(data_model, update, context):
    """
    Entry point for training controller.

    If plan has not been chosen, asks to choose one.
    If plan is chosen, shows workout.
    """

    user_id = update.message.from_user.id
    user_context = data_model.users.get_user_context(user_id)

    if (user_context.current_table_id is None
            or user_context.current_page is None):
        data_model.users.set_user_action(user_id, UserAction.CHOOSING_PLAN)
        await prompt_change_plan(data_model, update, context)
    else:
        data_model.users.set_user_action(user_id, UserAction.TRAINING)
        await send_workout(context.bot, data_model, user_context)


async def prompt_change_plan(data_model, update, context):
    """
    Asks the user with user_id to choose plan.
    """

    user_id = update.message.from_user.id
    user_context = data_model.users.get_user_context(user_id)
    chat_id = user_context.chat_id
    table_id = user_context.current_table_id

    if not table_id:
        await context.bot.send_message(chat_id,
                                       "Вам не назначена программа тренировок",
                                       reply_markup=ReplyKeyboardRemove()
                                       )
        data_model.users.set_user_action(user_id,
                                         UserAction.USER_NEEDS_PROGRAM)
        return

    if not data_model.workout_plans.is_table_id_present(table_id):
        await context.bot.send_message(chat_id,
                                       "Назначенная программа не существует",
                                       reply_markup=ReplyKeyboardRemove())
        data_model.users.set_user_action(user_id,
                                         UserAction.USER_NEEDS_PROGRAM)
        return

    plans = data_model.workout_plans.get_plan_names(table_id)
    if plans:
        keyboard = []
        text = 'Выберите программу из списка:\n'
        for plan in plans:
            text += '\n - ' + plan
            keyboard.append([KeyboardButton(plan, callback_data=plan)])
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await context.bot.send_message(chat_id,
                                       text,
                                       reply_markup=reply_markup)


async def send_all_actions(bot, chat_id):
    """
    Sends extended keyboard with all the keys.
    """

    keyboard = [
        [KeyboardButton("Сменить программу")],
        [
            KeyboardButton("Начальная неделя"),
            KeyboardButton("Последняя неделя")
        ],
        [
            KeyboardButton("Прошлая неделя"),
            KeyboardButton("Следующая неделя")
        ],
        [KeyboardButton("Следующая тренировка")],
        [KeyboardButton("Перейти к тренировкам")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await bot.send_message(chat_id,
                           "Доступные действия:",
                           reply_markup=reply_markup,
                           parse_mode="MarkdownV2")


async def send_with_next_or_all_buttons(bot, user_context, message):
    """
    Sends message and adds buttons "Далее", "Все действия"
    """

    chat_id = user_context.chat_id
    keyboard = [[KeyboardButton("Все действия"), KeyboardButton("Далее")]]
    if user_context.administrative_permission:
        key_admin = [KeyboardButton("Администрирование")]
        keyboard.append(key_admin)
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await bot.send_message(chat_id,
                           message,
                           disable_web_page_preview=True,
                           reply_markup=reply_markup,
                           parse_mode="MarkdownV2")


async def send_week_schedule(bot, data_model, user_context):
    """
    Sends week workout schedule.
    """

    message = get_week_routine_text_message(data_model,
                                            user_context.current_table_id,
                                            user_context.current_page,
                                            user_context.current_week)
    await send_with_next_or_all_buttons(bot, user_context, message)


async def send_workout(bot, data_model, user_context):
    """
    Sends workout.
    """

    message = get_workout_text_message(data_model,
                                       user_context.current_table_id,
                                       user_context.current_page,
                                       user_context.current_week,
                                       user_context.current_workout)
    await send_with_next_or_all_buttons(bot, user_context, message)


def handle_go_training():
    """
    Handles switch to training status.
    """

    def handler_filter(data_model, update):
        """
        The user needs to change plan if she is in TRAINING state and plan is
        not valid.
        """

        user_id = update.message.from_user.id
        user_context = data_model.users.get_user_context(user_id)
        message_text = update.message.text.strip().lower()
        return (user_context.action in (UserAction.TRAINING,
                                        UserAction.ADMINISTRATION,
                                        UserAction.ADMIN_TABLE_MANAGEMENT)
                and message_text == "перейти к тренировкам")

    async def handler(data_model, update, context):
        """
        Starts training.
        """

        await start_training(data_model, update, context)
        return True

    return (handler_filter, handler)


def handle_need_change_plan():
    """
    Handles any message, checks if the client needs to change plan.
    """

    def handler_filter(data_model, update):
        """
        The user needs to change plan if she is in TRAINING state and plan is
        not valid.
        """

        user_id = update.message.from_user.id
        user_context = data_model.users.get_user_context(user_id)
        message_text = update.message.text.strip().lower()
        table_id = user_context.current_table_id
        current_page = user_context.current_page
        pages = data_model.workout_plans.get_plan_names(table_id)
        return user_context.action == UserAction.TRAINING \
            and (user_context.current_page is None
                 or current_page not in pages
                 or message_text in ("выбрать программу",
                                     "сменить программу",
                                     "поменять программу"))

    async def handler(data_model, update, context):
        """
        If plan is not vlalid, change state to CHOOSING_PLAN and asks to choose
        correct plan.
        """

        user_id = update.message.from_user.id
        data_model.users.set_user_action(user_id, UserAction.CHOOSING_PLAN)
        await prompt_change_plan(data_model, update, context)
        return True

    return (handler_filter, handler)


def handle_message_change_plan():
    """
    Handles messages in change plan state.
    """

    def handler_filter(data_model, update):
        """
        Checks if user in CHOOSING_PLAN state.
        """

        user_id = update.message.from_user.id
        user_context = data_model.users.get_user_context(user_id)
        return user_context.action == UserAction.CHOOSING_PLAN

    async def handler(data_model, update, context):
        """
        Changes plan to the selected one for the user.
        """

        new_plan = update.message.text
        user_id = update.message.from_user.id
        user_context = data_model.users.get_user_context(user_id)
        chat_id = user_context.chat_id
        table_id = user_context.current_table_id

        if data_model.workout_plans.is_plan_present(table_id, new_plan):
            user_context.current_page = new_plan
            user_context.current_week = data_model.workout_plans \
                .get_week_number(user_context.current_table_id,
                                 user_context.current_page) - 1
            user_context.current_workout = 0
            data_model.users.set_user_context(user_context)
            data_model.users.set_user_action(user_context.user_id,
                                             UserAction.TRAINING)
            await send_week_schedule(context.bot, data_model, user_context)
            await send_workout(context.bot, data_model, user_context)
        else:
            await context.bot.send_message(chat_id, "Нет такой программы")
            await prompt_change_plan(data_model, update, context)

    return (handler_filter, handler)


def handle_all_actions():
    """
    The user wants to display all possible actions in TRAINING status.
    """

    def handler_filter(data_model, update):
        """
        The user in TRAINING status
        """

        message_text = update.message.text.strip().lower()
        user_id = update.message.from_user.id
        user_context = data_model.users.get_user_context(user_id)
        return (user_context.action == UserAction.TRAINING
                and message_text == "все действия")

    async def handler(data_model, update, context):
        """
        Shows all possible actions.
        """

        _ = data_model

        chat_id = update.effective_chat.id
        await send_all_actions(context.bot, chat_id)
        return True

    return (handler_filter, handler)


def handle_next():
    """
    Handles messages in change plan state.
    """

    def handler_filter(data_model, update):
        """
        Checks if user in TRAINING state and sends "next".
        """

        message_text = update.message.text.strip().lower()
        user_id = update.message.from_user.id
        user_context = data_model.users.get_user_context(user_id)
        return (user_context.action == UserAction.TRAINING
                and (message_text in ("далее", "следующая тренировка")))

    async def handler(data_model, update, context):
        """
        Shows next workout.
        """

        user_id = update.message.from_user.id
        user_context = data_model.users.get_user_context(user_id)
        week_previous = user_context.current_week
        data_model.next_workout_for_user(user_id)
        if week_previous != user_context.current_week:
            # show week schedule if week changes
            await send_week_schedule(context.bot, data_model, user_context)
        await send_workout(context.bot, data_model, user_context)
        return True

    return (handler_filter, handler)


def handle_first_week():
    """
    The user wants to go to the first week.
    """

    def handler_filter(data_model, update):
        """
        The user in TRAINING status and presses go to the first week.
        """

        message_text = update.message.text.strip().lower()
        user_id = update.message.from_user.id
        user_context = data_model.users.get_user_context(user_id)
        return (user_context.action == UserAction.TRAINING
                and message_text in ("первая неделя", "начальная неделя"))

    async def handler(data_model, update, context):
        """
        Shows all possible actions.
        """

        user_id = update.message.from_user.id
        user_context = data_model.users.get_user_context(user_id)

        user_context.current_week = 0
        user_context.current_workout = 0
        data_model.users.set_user_context(user_context)
        await send_week_schedule(context.bot, data_model, user_context)
        await send_workout(context.bot, data_model, user_context)
        return True

    return (handler_filter, handler)


def handle_last_week():
    """
    The user wants to go to the last week.
    """

    def handler_filter(data_model, update):
        """
        The user in TRAINING status and presses go to the last week.
        """

        message_text = update.message.text.strip().lower()
        user_id = update.message.from_user.id
        user_context = data_model.users.get_user_context(user_id)
        return (user_context.action == UserAction.TRAINING
                and message_text in ("последняя неделя", "крайняя неделя",
                                     "текущая неделя"))

    async def handler(data_model, update, context):
        """
        Shows all possible actions.
        """

        user_id = update.message.from_user.id
        user_context = data_model.users.get_user_context(user_id)

        user_context.current_week = data_model.workout_plans \
            .get_week_number(user_context.current_table_id,
                             user_context.current_page) - 1
        user_context.current_workout = 0
        data_model.users.set_user_context(user_context)
        await send_week_schedule(context.bot, data_model, user_context)
        await send_workout(context.bot, data_model, user_context)
        return True

    return (handler_filter, handler)


def handle_next_week():
    """
    The user wants to go to the last week.
    """

    def handler_filter(data_model, update):
        """
        The user in TRAINING status and presses go to the next week.
        """

        message_text = update.message.text.strip().lower()
        user_id = update.message.from_user.id
        user_context = data_model.users.get_user_context(user_id)
        return (user_context.action == UserAction.TRAINING
                and message_text in ("следующая неделя"))

    async def handler(data_model, update, context):
        """
        Shows all possible actions.
        """

        user_id = update.message.from_user.id
        user_context = data_model.users.get_user_context(user_id)

        if user_context.current_week < data_model.workout_plans \
                .get_week_number(user_context.current_table_id,
                                 user_context.current_page) - 1:
            user_context.current_week += 1
        user_context.current_workout = 0
        data_model.users.set_user_context(user_context)
        await send_week_schedule(context.bot, data_model, user_context)
        await send_workout(context.bot, data_model, user_context)
        return True

    return (handler_filter, handler)


def handle_previous_week():
    """
    The user wants to go to the last week.
    """

    def handler_filter(data_model, update):
        """
        The user in TRAINING status and presses go to the previous week.
        """

        message_text = update.message.text.strip().lower()
        user_id = update.message.from_user.id
        user_context = data_model.users.get_user_context(user_id)
        return (user_context.action == UserAction.TRAINING
                and message_text in ("прошлая неделя", "предыдущая неделя"))

    async def handler(data_model, update, context):
        """
        Shows all possible actions.
        """

        user_id = update.message.from_user.id
        user_context = data_model.users.get_user_context(user_id)

        if user_context.current_week > 0:
            user_context.current_week -= 1
        user_context.current_workout = 0
        data_model.users.set_user_context(user_context)
        await send_week_schedule(context.bot, data_model, user_context)
        await send_workout(context.bot, data_model, user_context)
        return True

    return (handler_filter, handler)


table_management_message_handlers = [
    handle_go_training(),
    handle_need_change_plan(),
    handle_message_change_plan(),
    handle_all_actions(),
    handle_next(),
    handle_first_week(),
    handle_last_week(),
    handle_next_week(),
    handle_previous_week()
]
