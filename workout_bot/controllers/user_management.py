"""
Provides user interaction for user manamegent.
"""

from telegram import KeyboardButton, ReplyKeyboardMarkup
from data_model.users import UserAction, BlockUserContext
from data_model.users import AssignTableUserContext
from view.users import get_user_message
from view.users import (
    user_to_text_message, user_to_short_text_message
)
from view.utils import escape_text
from telegram_bot.utils import get_user_context


async def send_with_user_management_panel(
        bot,
        chat_id,
        text="Управление пользователями"
):
    """
    Shows user management panel.
    """

    keyboard = [
        [KeyboardButton("Авторизация пользователей")],
        [KeyboardButton("Показать всех")],
        [KeyboardButton("Добавить администратора")],
        [KeyboardButton("Администрирование")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await bot.send_message(chat_id,
                           text,
                           reply_markup=reply_markup,
                           parse_mode="MarkdownV2")


async def show_users_authorization(bot, data_model, chat_id, user_context):
    """
    Shows user authorization.
    """

    users_in_line = data_model.users.get_users_awaiting_authorization()
    if not users_in_line:
        data_model.users.set_user_action(
            user_context.user_id,
            UserAction.ADMIN_USER_MANAGEMENT
        )
        await send_with_user_management_panel(
            bot,
            chat_id,
            text="Никто не ждёт авторизации"
        )
        return
    text = "Ожидают авторизации:\n"
    keyboard = []
    for user in users_in_line:
        text += " \\- " + user_to_text_message(user) + "\n"
        username = user_to_short_text_message(user)
        keyboard.append([
            KeyboardButton(text="Блокировать " + username),
            KeyboardButton(text="Авторизовать " + username),
            KeyboardButton(text="Отмена")
        ])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await bot.send_message(
        chat_id,
        text,
        reply_markup=reply_markup,
        parse_mode="MarkdownV2"
    )


async def show_all_users(bot, chat_id, data_model):
    """
    Shows all the users.
    """

    text = ""

    waiting_authorization = set()
    blocked = set()
    others = set()

    for user in data_model.users.get_all_users():
        if user.action == UserAction.BLOCKED:
            blocked.add(user)
        elif user.action == UserAction.AWAITING_AUTHORIZATION:
            waiting_authorization.add(user)
        else:
            others.add(user)

    if waiting_authorization:
        text += "Ожидают авторизации:\n"
        for user in waiting_authorization:
            text += " \\- " + user_to_text_message(user) + "\n"
        text += "\n"
    if others:
        text += "Тренируются:\n"
        for user in others:
            plan_name = escape_text(
                data_model.workout_plans.get_plan_name(user.current_table_id)
            )
            text += f" \\- {user_to_text_message(user)}"
            if user.administrative_permission:
                text += " \\- *администратор*"
            text += f" \\- {plan_name}"
            text += f" \\- неделя: {user.current_week}"
            text += "\n"
        text += "\n"
    if blocked:
        text += "Заблокрироанные:\n"
        for user in blocked:
            text += " \\- " + user_to_text_message(user) + "\n"

    await send_with_user_management_panel(bot, chat_id, text)


async def prompt_assign_table(
        bot,
        chat_id,
        data_model,
        target_username,
        text=""):
    """
    Asks to assign a table to the user with user_context.
    """
    if text:
        text += "\n"
    text += f"Какую таблицу назначим для {target_username}?\n\n"
    keyboard = []
    for table_name in data_model.workout_plans.get_table_names():
        text += " \\- " + escape_text(table_name) + "\n"
        key_tale_name = [KeyboardButton(text=table_name)]
        keyboard.append(key_tale_name)
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await bot.send_message(chat_id, text,
                           reply_markup=reply_markup,
                           parse_mode="MarkdownV2")


async def prompt_confirm_block(bot, chat_id, target_username):
    """
    Asks to confirm user blocking.
    """

    text = f"Заблокировать пользователя {escape_text(target_username)}?"
    keyboard = [[KeyboardButton("Нет"), KeyboardButton("Да")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await bot.send_message(chat_id, text, reply_markup=reply_markup)


async def prompt_add_admin(bot, chat_id, data_model):
    """
    Asks to assign administrative_permission to the user with user_context.
    """

    text = "Кому дать права администратора?\n"
    keyboard = []
    users = data_model.users.get_potential_admins()
    for user in users:
        text += " \\- " + user_to_text_message(user) + "\n"
        username = user_to_short_text_message(user)
        key = [KeyboardButton(text=username)]
        keyboard.append(key)
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await bot.send_message(
        chat_id,
        text,
        reply_markup=reply_markup,
        parse_mode="MarkdownV2"
    )


def handle_go_user_management():
    """
    Handles switch to user management.
    """

    def handler_filter(data_model, update):
        """
        The admin sends go to user management message.
        """

        user_context = get_user_context(data_model, update)
        message_text = update.message.text.strip().lower()
        return (user_context.administrative_permission and
                user_context.action in (UserAction.TRAINING,
                                        UserAction.ADMINISTRATION,
                                        UserAction.ADMIN_USER_MANAGEMENT)
                and message_text == "управление пользователями")

    async def handler(data_model, update, context):
        """
        Shows user management panel and sets user state.
        """

        user_context = get_user_context(data_model, update)
        data_model.users.set_user_action(user_context.user_id,
                                         UserAction.ADMIN_USER_MANAGEMENT)
        await send_with_user_management_panel(
            context.bot,
            update.effective_chat.id
        )

    return handler_filter, handler


def handle_go_user_authorization():
    """
    User authorization handler.
    """

    def handler_filter(data_model, update):
        """
        The admin sends authorize user message.
        """

        user_context = get_user_context(data_model, update)
        message_text = update.message.text.strip().lower()
        return (user_context.administrative_permission and
                user_context.action == UserAction.ADMIN_USER_MANAGEMENT and
                message_text == "авторизация пользователей")

    async def handler(data_model, update, context):
        """
        Asks which user to authorize.
        """

        user_context = get_user_context(data_model, update)
        data_model.users.set_user_action(user_context.user_id,
                                         UserAction.ADMIN_USER_AUTHORIZATION)
        await show_users_authorization(
            context.bot,
            data_model,
            update.effective_chat.id,
            user_context
        )

    return handler_filter, handler


def handle_authorize_user_cancel():
    """
    Admin cancels user authorization.
    """

    def handler_filter(data_model, update):
        """
        The admin sends cancels when authorizing the user.
        """

        user_context = get_user_context(data_model, update)
        message_text = update.message.text.strip().lower()
        return (user_context.administrative_permission and
                user_context.action == UserAction.ADMIN_USER_AUTHORIZATION and
                message_text.startswith("отмена"))

    async def handler(data_model, update, context):
        """
        Admin state is changed to user management.
        """

        user_context = get_user_context(data_model, update)
        data_model.users.set_user_action(
            user_context.user_id, UserAction.ADMIN_USER_MANAGEMENT)
        await send_with_user_management_panel(
            context.bot,
            update.effective_chat.id
        )

    return handler_filter, handler


def handle_authorize_user():
    """
    Admin authorizing user.
    """

    def handler_filter(data_model, update):
        """
        The admin chooses user to authorize.
        """

        user_context = get_user_context(data_model, update)
        message_text = update.message.text.strip().lower()
        return (user_context.administrative_permission and
                user_context.action == UserAction.ADMIN_USER_AUTHORIZATION and
                message_text.startswith("авторизовать "))

    async def handler(data_model, update, context):
        """
        Admin authorizes user and go to table assignment.
        """

        user_context = get_user_context(data_model, update)
        chat_id = user_context.chat_id
        short_username = update.message.text.strip()[13:]
        target_user_context = \
            data_model.users.get_user_context_by_short_username(short_username)
        if target_user_context is None:
            await context.bot.send_message(chat_id, "Нет такого пользователя")
            await send_with_user_management_panel(context.bot, chat_id)
        else:
            data_model.users.set_user_action(
                user_context.user_id, UserAction.ADMIN_USER_ASSIGNING_TABLE)
            data_model.users.set_user_input_data(
                user_context.user_id,
                AssignTableUserContext(target_user_context.user_id)
            )
            target_username = user_to_text_message(
                target_user_context
            )
            await prompt_assign_table(context.bot,
                                      chat_id,
                                      data_model,
                                      target_username)

    return handler_filter, handler


def handle_assign_table():
    """
    Handles table assigning to the user.
    """

    def handler_filter(data_model, update):
        """
        The admin chooses table to assign to the user.
        """

        user_context = get_user_context(data_model, update)
        table_name = update.message.text.strip()
        return (user_context.administrative_permission and
                user_context.action == UserAction.ADMIN_USER_ASSIGNING_TABLE
                and table_name in data_model.workout_plans.get_table_names())

    async def handler(data_model, update, context):
        """
        Admin assigns table, the user is notified.
        """

        user_context = get_user_context(data_model, update)
        table_name = update.message.text
        target_user_id = user_context.user_input_data.user_id
        table_id = data_model.workout_plans.get_table_id_by_name(table_name)
        data_model.users.set_table_for_user(target_user_id, table_id)
        data_model.users.set_user_action(
            target_user_id,
            UserAction.CHOOSING_PLAN
        )
        # notify target user
        target_user_context = data_model.users.get_user_context(target_user_id)
        text = f"Назначена программа тренировок *{escape_text(table_name)}*\n"
        text += "\n"
        text += "Для продолжения нажмите \"Перейти к тренировкам\""
        keyboard = [["Перейти к тренировкам"]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
        await context.bot.send_message(
            target_user_context.chat_id,
            text,
            disable_notification=True,
            reply_markup=reply_markup,
            parse_mode="MarkdownV2"
        )

        user_context.action = UserAction.ADMIN_USER_MANAGEMENT
        user_context.user_input_data = None
        data_model.users.set_user_context(user_context)
        await send_with_user_management_panel(
            context.bot,
            update.effective_chat.id
        )

    return handler_filter, handler


def handle_assign_wrong_table():
    """
    Handles wrong table name assigning to the user.
    """

    def handler_filter(data_model, update):
        """
        The admin chooses table to assign to the user.
        """

        user_context = get_user_context(data_model, update)
        table_name = update.message.text
        return (user_context.administrative_permission and
                user_context.action == UserAction.ADMIN_USER_ASSIGNING_TABLE
                and
                table_name not in data_model.workout_plans.get_table_names())

    async def handler(data_model, update, context):
        """
        Shows assign table message again.
        """

        user_context = get_user_context(data_model, update)
        target_user_context = data_model\
            .users.get_user_context(user_context.user_input_data.user_id)
        target_username = user_to_text_message(target_user_context)
        table_name = update.message.text.strip()
        await prompt_assign_table(
            context.bot,
            user_context.chat_id,
            data_model,
            target_username,
            f"Нет таблицы с именем '{table_name}'."
        )

    return handler_filter, handler


def handle_block_user():
    """
    Admin blocking user.
    """

    def handler_filter(data_model, update):
        """
        The admin chooses user to block.
        """

        user_context = get_user_context(data_model, update)
        message_text = update.message.text.strip().lower()
        return (user_context.administrative_permission and
                user_context.action == UserAction.ADMIN_USER_AUTHORIZATION and
                message_text.startswith("блокировать "))

    async def handler(data_model, update, context):
        """
        Admin blocks user.
        """

        user_context = get_user_context(data_model, update)
        chat_id = user_context.chat_id
        short_username = update.message.text.strip()[12:]
        target_user_context = \
            data_model.users.get_user_context_by_short_username(short_username)
        if target_user_context is None:
            await context.bot.send_message(
                chat_id,
                "Нет такого пользователя"
            )
            await send_with_user_management_panel(context.bot, chat_id)
        else:
            user_context.action = UserAction.ADMIN_USER_BLOCKING
            user_context.user_input_data = \
                BlockUserContext(target_user_context.user_id)
            data_model.users.set_user_context(user_context)
            target_username = user_to_text_message(
                data_model
                .users
                .get_user_context(user_context.user_input_data.user_id)
            )
            await prompt_confirm_block(
                context.bot,
                chat_id,
                target_username
            )

    return handler_filter, handler


def handle_confirm_block_yes():
    """
    Handler for user blocking confirmation.
    """

    def handler_filter(data_model, update):
        """
        The admin is in ADMIN_USER_BLOCKING state and presses Yes.
        """

        user_context = get_user_context(data_model, update)
        message_text = update.message.text.strip().lower()
        return (user_context.administrative_permission and
                user_context.action == UserAction.ADMIN_USER_BLOCKING and
                message_text == "да")

    async def handler(data_model, update, context):
        """
        Admin blocks user.
        """

        user_context = get_user_context(data_model, update)
        chat_id = user_context.chat_id
        target_username = get_user_message(
            data_model,
            user_context.user_input_data.user_id
        )
        data_model.users.block_user(user_context.user_input_data.user_id)
        user_context.action = UserAction.ADMIN_USER_MANAGEMENT
        user_context.user_input_data = None
        data_model.users.set_user_context(user_context)
        await context.bot.send_message(
            chat_id,
            f"{target_username} заблокирован."
        )
        await send_with_user_management_panel(context.bot, chat_id)

    return handler_filter, handler


def handle_confirm_block_no():
    """
    Handler for user blocking denial.
    """

    def handler_filter(data_model, update):
        """
        The admin is in ADMIN_USER_BLOCKING state and presses No.
        """

        user_context = get_user_context(data_model, update)
        message_text = update.message.text.strip().lower()
        return (user_context.administrative_permission and
                user_context.action == UserAction.ADMIN_USER_BLOCKING and
                message_text == "нет")

    async def handler(data_model, update, context):
        """
        Admin does not block user.
        """

        user_context = get_user_context(data_model, update)
        chat_id = user_context.chat_id
        user_context.action = UserAction.ADMIN_USER_MANAGEMENT
        user_context.user_input_data = None
        data_model.users.set_user_context(user_context)
        await send_with_user_management_panel(context.bot, chat_id)

    return handler_filter, handler


def handle_confirm_block_unrecognized():
    """
    Handler for user blocking unrecognized input.
    """

    def handler_filter(data_model, update):
        """
        The admin is in ADMIN_USER_BLOCKING state and inputs unrecognized text.
        """

        user_context = get_user_context(data_model, update)
        return (user_context.administrative_permission and
                user_context.action == UserAction.ADMIN_USER_BLOCKING)

    async def handler(data_model, update, context):
        """
        Show block confirmation.
        """

        user_context = get_user_context(data_model, update)
        target_username = user_to_text_message(
            data_model.users.get_user_context(
                user_context.user_input_data.user_id
            )
        )
        await prompt_confirm_block(
            context.bot,
            user_context.chat_id,
            target_username
        )

    return handler_filter, handler


def handle_show_all_users():
    """
    Show all users message handler.
    """

    def handler_filter(data_model, update):
        """
        The admin sends show all users message.
        """

        user_context = get_user_context(data_model, update)
        message_text = update.message.text.strip().lower()
        return (user_context.administrative_permission and
                user_context.action == UserAction.ADMIN_USER_MANAGEMENT and
                message_text == "показать всех")

    async def handler(data_model, update, context):
        """
        Shows all users.
        """

        user_context = get_user_context(data_model, update)
        await show_all_users(context.bot, user_context.chat_id, data_model)

    return handler_filter, handler


def handle_add_admin():
    """
    Add admin message handler.
    """

    def handler_filter(data_model, update):
        """
        The admin sends add admin message.
        """

        user_context = get_user_context(data_model, update)
        message_text = update.message.text.strip().lower()
        return (user_context.administrative_permission and
                user_context.action == UserAction.ADMIN_USER_MANAGEMENT and
                message_text == "добавить администратора")

    async def handler(data_model, update, context):
        """
        Prompts add admin.
        """

        user_context = get_user_context(data_model, update)
        potential_admins = data_model.users.get_potential_admins()
        if potential_admins:
            data_model.users.set_user_action(user_context.user_id,
                                             UserAction.ADMIN_ADDING_ADMIN)
            await prompt_add_admin(
                context.bot,
                user_context.chat_id,
                data_model
            )
        else:
            data_model.users.set_user_action(user_context.user_id,
                                             UserAction.ADMIN_USER_MANAGEMENT)
            await send_with_user_management_panel(
                context.bot,
                update.effective_chat.id,
                text="Некого назначить администратором"
            )

    return handler_filter, handler


def handle_add_admin_input():
    """
    Admin adds admin.
    """

    def handler_filter(data_model, update):
        """
        The admin sends username to grant administrative permissions.
        """

        user_context = get_user_context(data_model, update)
        message_text = update.message.text.strip().lower()
        new_admin = data_model.users.get_user_context_by_short_username(
            message_text
        )
        return (user_context.administrative_permission and
                user_context.action == UserAction.ADMIN_ADDING_ADMIN and
                new_admin is not None)

    async def handler(data_model, update, context):
        """
        Adds admin.
        """

        user_context = get_user_context(data_model, update)
        message_text = update.message.text.strip().lower()
        new_admin = data_model.users.get_user_context_by_short_username(
            message_text
        )
        data_model.users.set_administrative_permission(new_admin.user_id)
        user_context.action = UserAction.ADMIN_USER_MANAGEMENT
        user_context.user_input_data = None
        data_model.users.set_user_context(user_context)
        await send_with_user_management_panel(
            context.bot,
            update.effective_chat.id
        )

    return handler_filter, handler


def handle_add_admin_wrong_input():
    """
    Admin adds admin.
    """

    def handler_filter(data_model, update):
        """
        The admin sends wrong username.
        """

        user_context = get_user_context(data_model, update)
        message_text = update.message.text.strip().lower()
        new_admin = data_model.users.get_user_context_by_short_username(
            message_text
        )
        return (user_context.administrative_permission and
                user_context.action == UserAction.ADMIN_ADDING_ADMIN and
                new_admin is None)

    async def handler(data_model, update, context):
        """
        Ask again.
        """

        user_context = get_user_context(data_model, update)
        data_model.users.set_user_action(
            user_context.user_id,
            UserAction.ADMIN_USER_MANAGEMENT
        )
        await send_with_user_management_panel(
            context.bot,
            update.effective_chat.id,
            text="Нет такого пользователя"
        )

    return handler_filter, handler


user_management_message_handlers = [
    handle_go_user_management(),
    handle_go_user_authorization(),
    handle_authorize_user_cancel(),
    handle_assign_table(),
    handle_assign_wrong_table(),
    handle_block_user(),
    handle_authorize_user(),
    handle_confirm_block_yes(),
    handle_confirm_block_no(),
    handle_confirm_block_unrecognized(),
    handle_show_all_users(),
    handle_add_admin(),
    handle_add_admin_input(),
    handle_add_admin_wrong_input()
]
