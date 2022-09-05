"""
Provides user interaction for administation process.
"""

from telegram import Update
from telegram import KeyboardButton, ReplyKeyboardMarkup
from data_model.users import UserAction


async def show_admin_panel(bot, chat_id, user_context):
    """
    Shows administation panel.
    """

    if user_context.administrative_permission:
        keyboard = [
            [KeyboardButton("Управление пользователями")],
            [KeyboardButton("Управление таблицами")],
            [KeyboardButton("Перейти к тренировкам")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await bot.send_message(chat_id, "Администрирование",
                               reply_markup=reply_markup,
                               parse_mode="MarkdownV2")


def handle_go_administration():
    """
    Handles go to administration.
    """

    def handler_filter(data_model, update):
        """
        Admin in ADMIN_TABLE_MANAGEMENT state.
        """
        user_id = update.message.from_user.id
        user_context = data_model.users.get_user_context(user_id)
        message_text = update.message.text.strip().lower()
        return (user_context.action == UserAction.ADMIN_TABLE_MANAGEMENT
                and message_text == "администрирование")

    async def handler(data_model, update, context):
        """
        Handle other messages.
        """

        user_id = update.message.from_user.id
        user_context = data_model.users.get_user_context(user_id)
        chat_id = user_context.chat_id
        data_model.users.set_user_action(user_id, UserAction.ADMINISTRATION)
        await show_admin_panel(context.bot, chat_id, user_context)
        return True

    return (handler_filter, handler)


administration_message_handlers = [
    handle_go_administration()
]


class Administration:
    """
    Provides user interaction for administation process.
    """

    def __init__(self, bot, data_model):
        self.bot = bot
        self.data_model = data_model

    async def show_admin_panel(self, chat_id, user_context):
        """
        Shows administation panel.
        """

        if user_context.administrative_permission:
            keyboard = [
                [KeyboardButton("Управление пользователями")],
                [KeyboardButton("Управление таблицами")],
                [KeyboardButton("Перейти к тренировкам")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await self.bot.send_message(chat_id, "Администрирование",
                                        reply_markup=reply_markup,
                                        parse_mode="MarkdownV2")

    async def handle_message(self, update: Update):
        """
        Handles text messages related to administration.
        """

        user_context = \
            self.data_model.users.get_user_context(update.message.from_user.id)
        message_text = update.message.text.strip().lower()

        if user_context is None or not user_context.administrative_permission:
            return False

        # change user action commands
        if user_context.action == UserAction.ADMINISTRATION:
            if message_text == "перейти к тренировкам":
                # return to above menu
                return False

            await self.show_admin_panel(update.effective_chat.id, user_context)
            return True

        return False
