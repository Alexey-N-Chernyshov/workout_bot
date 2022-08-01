"""
Provides user interaction for user manamegent.
"""

from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from data_model.users import UserAction, BlockUserContext
from data_model.users import AssignTableUserContext
from view.users import get_user_message
from view.users import user_to_text_message, user_to_short_text_message


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

    def show_user_management_panel(self, chat_id,
                                   text="Управление пользователями"):
        """
        Shows user management panel.
        """

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                       one_time_keyboard=True)
        key_user_authz = KeyboardButton(text="Авторизация пользователей")
        keyboard.add(key_user_authz)
        key_show_all = KeyboardButton(text="Показать всех")
        keyboard.add(key_show_all)
        key_add_admin = KeyboardButton(text="Добавить администратора")
        keyboard.add(key_add_admin)
        key_administration = KeyboardButton(text="Администрирование")
        keyboard.add(key_administration)
        self.bot.send_message(chat_id, text,
                              reply_markup=keyboard,
                              parse_mode="MarkdownV2")

    def show_user_authorization(self, chat_id, user_context):
        """
        Shows user authorization.
        """

        users_in_line = \
            self.data_model.users.get_users_awaiting_authorization()
        if not users_in_line:
            self.data_model.users\
                .set_user_action(user_context.user_id,
                                 UserAction.ADMIN_USER_MANAGEMENT)
            self.show_user_management_panel(chat_id,
                                            text="Никто не ждёт авторизации")
            return
        text = "Ожидают авторизации:\n"
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                       one_time_keyboard=True)
        for user in users_in_line:
            text += " \\- " + user_to_text_message(user) + "\n"
            username = user_to_short_text_message(user)
            key_block = KeyboardButton(text="Блокировать " + username)
            key_authorize = KeyboardButton(text="Авторизовать " + username)
            keyboard.row(key_block, key_authorize)

        self.bot.send_message(chat_id, text, reply_markup=keyboard,
                              parse_mode="MarkdownV2")

    def prompt_confirm_block(self, chat_id, user_context):
        """
        Asks to confirm user blocking.
        """

        username = user_to_text_message(
                self.data_model
                    .users
                    .get_user_context(user_context.user_input_data.user_id)
            )
        text = f"Заблокировать пользователя {username}?\n\n"
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        key_no = KeyboardButton(text="Нет")
        key_yes = KeyboardButton(text="Да")
        keyboard.row(key_no, key_yes)
        self.bot.send_message(chat_id, text,
                              reply_markup=keyboard)

    def prompt_assign_table(self, chat_id, user_context):
        """
        Asks to assign a table to the user with user_context.
        """

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        username = user_to_text_message(
                self.data_model
                    .users
                    .get_user_context(user_context.user_input_data.user_id)
            )
        text = f"Какую таблицу назначим для {username}?\n\n"
        for table_name in self.data_model.workout_plans.get_table_names():
            text += " \\- " + table_name + "\n"
            key_talbe_name = KeyboardButton(text=table_name)
            keyboard.add(key_talbe_name)
        self.bot.send_message(chat_id, text,
                              reply_markup=keyboard,
                              parse_mode="MarkdownV2")

    def prompt_add_admin(self, chat_id):
        """
        Asks to assign administrative_permission to the user with user_context.
        """

        text = "Кому дать права администратора?\n"
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                       one_time_keyboard=True)
        users = self.data_model.users.get_potential_admins()
        for user in users:
            text += " \\- " + user_to_text_message(user) + "\n"
            username = user_to_short_text_message(user)
            key = KeyboardButton(text=username)
            keyboard.add(key)
        self.bot.send_message(chat_id, text, reply_markup=keyboard,
                              parse_mode="MarkdownV2")

    def show_all_users(self, chat_id):
        """
        Shows all the users.
        """

        text = ""

        waiting_authorization = set()
        blocked = set()
        others = set()

        for user in self.data_model.users.get_all_users():
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
                plan_name = self.data_model \
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

        self.show_user_management_panel(chat_id, text)

    def handle_message(self, message):
        """
        Handles messages related to user management.
        Returns True if messsage was processed, False otherwise.
        """

        user_context = \
            self.data_model.users.get_user_context(message.from_user.id)
        chat_id = message.chat.id
        message_text = message.text.strip().lower()

        if user_context is None or not user_context.administrative_permission:
            return False

        if user_context.action == UserAction.ADMIN_USER_AUTHORIZATION:
            if message_text.startswith("блокировать "):
                short_username = message_text[12:]
                target_user_context = \
                    self.get_user_context_from_short_username(short_username)
                if target_user_context is None:
                    self.bot.send_message(chat_id, "Нет такого пользователя.")
                    self.show_user_management_panel(chat_id)
                    return True
                user_context.action = UserAction.ADMIN_USER_BLOCKING
                user_context.user_input_data = \
                    BlockUserContext(target_user_context.user_id)
                self.data_model.users.set_user_context(user_context)
                self.prompt_confirm_block(chat_id, user_context)
                return True
            if message_text.startswith("авторизовать "):
                short_username = message_text[13:]
                target_user_context = \
                    self.get_user_context_from_short_username(short_username)
                if target_user_context is None:
                    self.bot.send_message(chat_id, "Нет такого пользователя.")
                    self.show_user_management_panel(chat_id)
                    return True
                user_context.action = UserAction.ADMIN_USER_ASSIGNING_TABLE
                user_context.user_input_data = \
                    AssignTableUserContext(target_user_context.user_id)
                self.data_model.users.set_user_context(user_context)
                self.prompt_assign_table(chat_id, user_context)
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
                self.bot.send_message(chat_id,
                                      f"{target_username} заблокрирован.")
                self.show_user_management_panel(chat_id)
            elif message_text == "нет":
                user_context.action = UserAction.ADMIN_USER_MANAGEMENT
                user_context.user_input_data = None
                self.data_model.users.set_user_context(user_context)
                self.show_user_management_panel(chat_id)
            else:
                self.prompt_confirm_block(chat_id, user_context)
            return True

        if user_context.action == UserAction.ADMIN_USER_ASSIGNING_TABLE:
            table_name = message.text
            if table_name in self.data_model.workout_plans.get_table_names():
                target_user_id = user_context.user_input_data.user_id
                table_id = self.data_model \
                    .workout_plans.get_table_id_by_name(table_name)
                self.data_model.users.set_table_for_user(target_user_id,
                                                         table_id)
                self.data_model.users.set_user_action(target_user_id,
                                                      UserAction.CHOOSING_PLAN)
                user_context.action = UserAction.ADMIN_USER_MANAGEMENT
                user_context.user_input_data = None
                self.data_model.users.set_user_context(user_context)
                self.show_user_management_panel(chat_id)
            else:
                self.prompt_assign_table(chat_id, user_context)
            return True

        if user_context.action == UserAction.ADMIN_ADDING_ADMIN:
            new_admin = \
                self.get_user_context_from_short_username(message_text)
            if new_admin is None:
                self.data_model.users\
                    .set_user_action(user_context.user_id,
                                     UserAction.ADMIN_USER_MANAGEMENT)
                self.show_user_management_panel(chat_id,
                                                text="Нет такого пользователя")
                return True
            self.data_model \
                .users.set_administrative_permission(new_admin.user_id)
            user_context.action = UserAction.ADMIN_USER_MANAGEMENT
            user_context.user_input_data = None
            self.data_model.users.set_user_context(user_context)
            self.show_user_management_panel(chat_id)
            return True

        if user_context.action == UserAction.ADMIN_USER_MANAGEMENT:
            if message_text == "авторизация пользователей":
                self.data_model.users \
                    .set_user_action(user_context.user_id,
                                     UserAction.ADMIN_USER_AUTHORIZATION)
                self.show_user_authorization(chat_id, user_context)
                return True

            if message_text == "показать всех":
                self.show_all_users(chat_id)
                return True

            if message_text == "добавить администратора":
                self.data_model.users \
                    .set_user_action(user_context.user_id,
                                     UserAction.ADMIN_ADDING_ADMIN)
                self.prompt_add_admin(chat_id)
                return True

            if message_text == "администрирование":
                # return to above menu
                return False

        return False