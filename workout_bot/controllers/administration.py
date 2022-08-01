"""
Provides user interaction for administation process.
"""

from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from data_model.users import UserAction
from data_model.users import RemoveExcerciseLinkContext
from data_model.users import AddExcerciseLinkContext


class Administration:
    """
    Provides user interaction for administation process.
    """

    def __init__(self, bot, data_model):
        self.bot = bot
        self.data_model = data_model

    def show_admin_panel(self, chat_id, user_context):
        """
        Shows administation panel.
        """

        if user_context.administrative_permission:
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                           one_time_keyboard=True)
            key_user_management = KeyboardButton(
                text="Управление пользователями")
            keyboard.add(key_user_management)
            key_table_management = KeyboardButton(text="Управление таблицами")
            keyboard.add(key_table_management)
            key_remove_workout_link = \
                KeyboardButton(text="Удалить ссылку на упражнение")
            key_add_workout_link = \
                KeyboardButton(text="Добавить ссылку на упражнение")
            keyboard.row(key_remove_workout_link, key_add_workout_link)
            key_training = KeyboardButton(text='Перейти к тренировкам')
            keyboard.add(key_training)
            self.bot.send_message(chat_id, "Администрирование",
                                  reply_markup=keyboard,
                                  parse_mode="MarkdownV2")

    def remove_excercise_link_prompt(self, chat_id, user_context):
        """
        Asks to remove excercise link.
        """

        name = user_context.user_input_data.name
        link = self.data_model.excercise_links[name]
        text = f"Удалить упражнение?\n\n[{name}]({link})"
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        key_no = KeyboardButton(text="Нет")
        key_yes = KeyboardButton(text="Да")
        keyboard.row(key_no, key_yes)
        self.bot.send_message(chat_id, text, disable_web_page_preview=True,
                              reply_markup=keyboard, parse_mode="MarkdownV2")

    def add_excercise_link_prompt(self, chat_id, user_context):
        """
        Asks to add excercise link.
        """

        name = user_context.user_input_data.name
        link = user_context.user_input_data.link
        text = f"Добавить упражнение?\n\n[{name}]({link})"
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        key_no = KeyboardButton(text="Нет")
        key_yes = KeyboardButton(text="Да")
        keyboard.row(key_no, key_yes)
        self.bot.send_message(chat_id, text, disable_web_page_preview=True,
                              reply_markup=keyboard, parse_mode="MarkdownV2")

    def handle_message(self, message):
        """
        Handles text messages related to administration.
        """

        user_context = \
            self.data_model.users.get_user_context(message.from_user.id)
        message_text = message.text.strip().lower()

        if user_context is None or not user_context.administrative_permission:
            return False

        if user_context.action == UserAction.ADMIN_REMOVING_EXCERCISE_NAME:
            name = message_text
            if name in self.data_model.excercise_links:
                user_context.user_input_data.name = name
                self.data_model.users.set_user_context(user_context)
                self.remove_excercise_link_prompt(message.chat.id,
                                                  user_context)
                user_context.action = UserAction.ADMIN_REMOVING_EXCERCISE_PROVE
            else:
                self.bot.send_message(message.chat.id, "Нет такого упражнения")
                self.data_model.users \
                    .set_user_action(user_context.user_id,
                                     UserAction.ADMINISTRATION)
                self.show_admin_panel(message.chat.id, user_context)
            return True

        if user_context.action == UserAction.ADMIN_REMOVING_EXCERCISE_PROVE:
            if message_text == "да":
                del self.data_model \
                    .excercise_links[user_context.user_input_data.name]
                user_context.action = UserAction.ADMINISTRATION
                user_context.user_input_data = None
                self.data_model.users.set_user_context(user_context)
                self.show_admin_panel(message.chat.id, user_context)
            elif message_text == "нет":
                user_context.action = UserAction.ADMINISTRATION
                user_context.user_input_data = None
                self.data_model.users.set_user_context(user_context)
                self.show_admin_panel(message.chat.id, user_context)
            else:
                self.remove_excercise_link_prompt(message.chat.id,
                                                  user_context)
            return True

        if user_context.action == UserAction.ADMIN_ADDING_EXCERCISE_NAME:
            user_context.action = UserAction.ADMIN_ADDING_EXCERCISE_LINK
            user_context.user_input_data.name = message_text
            self.data_model.users.set_user_context(user_context)
            self.bot.send_message(message.chat.id, "Введите ссылку")
            return True

        if user_context.action == UserAction.ADMIN_ADDING_EXCERCISE_LINK:
            user_context.action = UserAction.ADMIN_ADDING_EXCERCISE_PROVE
            user_context.user_input_data.link = message.text.strip()
            self.data_model.users.set_user_context(user_context)
            self.add_excercise_link_prompt(message.chat.id, user_context)
            return True

        if user_context.action == UserAction.ADMIN_ADDING_EXCERCISE_PROVE:
            if message_text == "да":
                self.data_model\
                    .excercise_links[user_context.user_input_data.name] = \
                    user_context.user_input_data.link
                user_context.action = UserAction.ADMINISTRATION
                user_context.user_input_data = None
                self.data_model.users.set_user_context(user_context)
                self.show_admin_panel(message.chat.id, user_context)
            elif message_text == "нет":
                user_context.action = UserAction.ADMINISTRATION
                user_context.user_input_data = None
                self.data_model.users.set_user_context(user_context)
                self.show_admin_panel(message.chat.id, user_context)
            else:
                self.add_excercise_link_prompt(message.chat.id, user_context)
            return True

        # change user action commands
        if user_context.action == UserAction.ADMINISTRATION:
            if message_text == "перейти к тренировкам":
                # return to above menu
                return False

            if message_text == "удалить ссылку на упражнение":
                user_context.action = UserAction.ADMIN_REMOVING_EXCERCISE_NAME
                user_context.user_input_data = RemoveExcerciseLinkContext()
                self.data_model.users.set_user_context(user_context)
                self.bot.send_message(message.chat.id,
                                      "Введите название упражнения")
                return True

            if message_text == "добавить ссылку на упражнение":
                user_context.action = UserAction.ADMIN_ADDING_EXCERCISE_NAME
                user_context.user_input_data = AddExcerciseLinkContext()
                self.data_model.users.set_user_context(user_context)
                self.bot.send_message(message.chat.id,
                                      "Введите название упражнения")
                return True

            self.show_admin_panel(message.chat.id, user_context)
            return True

        return False
