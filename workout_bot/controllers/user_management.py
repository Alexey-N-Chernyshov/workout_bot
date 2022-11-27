"""
Provides user interaction for user manamegent.
"""

from telegram import KeyboardButton, ReplyKeyboardMarkup
from data_model.users import UserAction, BlockUserContext
from data_model.users import AssignTableUserContext
from view.users import get_user_message
from view.users import user_to_text_message, user_to_short_text_message
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
            KeyboardButton(text="Авторизовать " + username)
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
            plan_name = data_model \
                .workout_plans.get_plan_name(user.current_table_id)
            text += f" \\- {user_to_text_message(user)} \\- {plan_name}"
            if user.administrative_permission:
                text += " \\- администратор"
            text += "\n"
        text += "\n"
    if blocked:
        text += "Заблокрироанные:\n"
        for user in blocked:
            text += " \\- " + user_to_text_message(user) + "\n"

    await send_with_user_management_panel(bot, chat_id, text)


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
        return True

    return handler_filter, handler


def handle_authorize_user():
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
        the admin sends add admin message.
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
        data_model.users.set_user_action(user_context.user_id,
                                         UserAction.ADMIN_ADDING_ADMIN)
        await prompt_add_admin(context.bot, user_context.chat_id, data_model)

    return handler_filter, handler


user_management_message_handlers = [
    handle_go_user_management(),
    handle_authorize_user(),
    handle_show_all_users(),
    handle_add_admin()
]


class UserManagement:
    """
    Provides user interaction for user manamegent.
    """

    def __init__(self, bot, data_model):
        self.bot = bot
        self.data_model = data_model

    def get_user_context_from_short_username(self, short_username):
        """
        Returns user_context from short username.
        """

        if short_username.startswith('@'):
            return self.data_model.users \
                .get_user_context_by_username(short_username)
        if short_username.startswith("id: "):
            try:
                return self.data_model.users \
                    .get_user_context(int(short_username[4:]))
            except Exception:
                return None
        return None

    async def show_user_management_panel(self, chat_id,
                                         text="Управление пользователями"):
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
        await self.bot.send_message(chat_id, text,
                                    reply_markup=reply_markup,
                                    parse_mode="MarkdownV2")

    async def prompt_confirm_block(self, chat_id, user_context):
        """
        Asks to confirm user blocking.
        """

        username = user_to_text_message(
                self.data_model
                    .users
                    .get_user_context(user_context.user_input_data.user_id)
            )
        text = f"Заблокировать пользователя {username}?"
        keyboard = [[KeyboardButton("Нет"), KeyboardButton("Да")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await self.bot.send_message(chat_id, text,
                                    reply_markup=reply_markup)

    async def prompt_assign_table(self, chat_id, user_context):
        """
        Asks to assign a table to the user with user_context.
        """

        username = user_to_text_message(
                self.data_model
                    .users
                    .get_user_context(user_context.user_input_data.user_id)
            )
        text = f"Какую таблицу назначим для {username}?\n\n"
        keyboard = []
        for table_name in self.data_model.workout_plans.get_table_names():
            text += " \\- " + table_name + "\n"
            key_talbe_name = [KeyboardButton(text=table_name)]
            keyboard.append(key_talbe_name)
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await self.bot.send_message(chat_id, text,
                                    reply_markup=reply_markup,
                                    parse_mode="MarkdownV2")

    async def handle_message(self, update, context):
        """
        Handles messages related to user management.
        Returns True if messsage was processed, False otherwise.
        """

        user_context = \
            self.data_model.users.get_user_context(update.message.from_user.id)
        chat_id = update.effective_chat.id
        message_text = update.message.text.strip().lower()

        if user_context is None or not user_context.administrative_permission:
            return False

        if user_context.action == UserAction.ADMIN_USER_AUTHORIZATION:
            if message_text.startswith("блокировать "):
                short_username = update.message.text.strip()[12:]
                target_user_context = \
                    self.get_user_context_from_short_username(short_username)
                if target_user_context is None:
                    await self.bot.send_message(chat_id,
                                                "Нет такого пользователя.")
                    await self.show_user_management_panel(chat_id)
                    return True
                user_context.action = UserAction.ADMIN_USER_BLOCKING
                user_context.user_input_data = \
                    BlockUserContext(target_user_context.user_id)
                self.data_model.users.set_user_context(user_context)
                await self.prompt_confirm_block(chat_id, user_context)
                return True
            if message_text.startswith("авторизовать "):
                short_username = update.message.text.strip()[13:]
                target_user_context = \
                    self.get_user_context_from_short_username(short_username)
                if target_user_context is None:
                    await self.bot.send_message(chat_id,
                                                "Нет такого пользователя.")
                    await self.show_user_management_panel(chat_id)
                    return True
                user_context.action = UserAction.ADMIN_USER_ASSIGNING_TABLE
                user_context.user_input_data = \
                    AssignTableUserContext(target_user_context.user_id)
                self.data_model.users.set_user_context(user_context)
                await self.prompt_assign_table(chat_id, user_context)
                return True

        if user_context.action == UserAction.ADMIN_USER_BLOCKING:
            if message_text == "да":
                target_username = get_user_message(
                        self.data_model,
                        user_context.user_input_data.user_id
                    )
                self.data_model \
                    .users.block_user(user_context.user_input_data.user_id)
                user_context.action = UserAction.ADMIN_USER_MANAGEMENT
                user_context.user_input_data = None
                self.data_model.users.set_user_context(user_context)
                await self.bot \
                    .send_message(chat_id,
                                  f"{target_username} заблокрирован.")
                await self.show_user_management_panel(chat_id)
            elif message_text == "нет":
                user_context.action = UserAction.ADMIN_USER_MANAGEMENT
                user_context.user_input_data = None
                self.data_model.users.set_user_context(user_context)
                await self.show_user_management_panel(chat_id)
            else:
                await self.prompt_confirm_block(chat_id, user_context)
            return True

        if user_context.action == UserAction.ADMIN_USER_ASSIGNING_TABLE:
            table_name = update.message.text
            if table_name in self.data_model.workout_plans.get_table_names():
                target_user_id = user_context.user_input_data.user_id
                table_id = self.data_model \
                    .workout_plans.get_table_id_by_name(table_name)
                self.data_model.users.set_table_for_user(target_user_id,
                                                         table_id)
                self.data_model.users.set_user_action(target_user_id,
                                                      UserAction.CHOOSING_PLAN)
                # notify target user
                target_user_context = self.data_model \
                    .users.get_user_context(target_user_id)
                text = f"Назначена программа тренировок *{table_name}*\n"
                text += "\n"
                text += "Для продолжения нажмите \"Перейти к тренировкам\""
                keyboard = [["Перейти к тренировкам"]]
                reply_markup = ReplyKeyboardMarkup(keyboard,
                                                   resize_keyboard=True)
                await context.bot.send_message(target_user_context.chat_id,
                                               text,
                                               disable_notification=True,
                                               reply_markup=reply_markup,
                                               parse_mode="MarkdownV2")

                user_context.action = UserAction.ADMIN_USER_MANAGEMENT
                user_context.user_input_data = None
                self.data_model.users.set_user_context(user_context)
                await self.show_user_management_panel(chat_id)
            else:
                await self.prompt_assign_table(chat_id, user_context)
            return True

        if user_context.action == UserAction.ADMIN_ADDING_ADMIN:
            new_admin = self.get_user_context_from_short_username(
                update.message.text.strip()
            )
            if new_admin is None:
                self.data_model.users\
                    .set_user_action(user_context.user_id,
                                     UserAction.ADMIN_USER_MANAGEMENT)
                await self \
                    .show_user_management_panel(chat_id,
                                                text="Нет такого пользователя")
                return True
            self.data_model \
                .users.set_administrative_permission(new_admin.user_id)
            user_context.action = UserAction.ADMIN_USER_MANAGEMENT
            user_context.user_input_data = None
            self.data_model.users.set_user_context(user_context)
            await self.show_user_management_panel(chat_id)
            return True

        return False
