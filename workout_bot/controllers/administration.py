"""
Provides user interaction for administation process.
"""

from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from data_model.users import UserAction


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
            key_training = KeyboardButton(text='Перейти к тренировкам')
            keyboard.add(key_training)
            self.bot.send_message(chat_id, "Администрирование",
                                  reply_markup=keyboard,
                                  parse_mode="MarkdownV2")

    def handle_message(self, message):
        """
        Handles text messages related to administration.
        """

        user_context = \
            self.data_model.users.get_user_context(message.from_user.id)
        message_text = message.text.strip().lower()

        if user_context is None or not user_context.administrative_permission:
            return False

        # change user action commands
        if user_context.action == UserAction.ADMINISTRATION:
            if message_text == "перейти к тренировкам":
                # return to above menu
                return False

            self.show_admin_panel(message.chat.id, user_context)
            return True

        return False
