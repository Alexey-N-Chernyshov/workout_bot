"""
Administration related messages handlers.
"""

from telegram import KeyboardButton, ReplyKeyboardMarkup
from workout_bot.data_model.users import UserAction
from workout_bot.telegram_bot.utils import get_user_context


async def show_admin_panel(bot, chat_id, user_context):
    """
    Shows administration panel.
    """

    if user_context.administrative_permission:
        keyboard = [
            [KeyboardButton("Управление пользователями")],
            [KeyboardButton("Управление таблицами")],
            [KeyboardButton("Перейти к тренировкам")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await bot.send_message(
            chat_id,
            "Администрирование",
            reply_markup=reply_markup,
            parse_mode="MarkdownV2"
        )


def handle_go_administration():
    """
    Handles go to administration.
    """

    def handler_filter(data_model, update):
        """
        Admin in ADMIN_TABLE_MANAGEMENT state.
        """
        user_context = get_user_context(data_model, update)
        message_text = update.message.text.strip().lower()
        return (user_context.action in (UserAction.ADMIN_USER_MANAGEMENT,
                                        UserAction.ADMIN_TABLE_MANAGEMENT,
                                        UserAction.TRAINING)
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

    return handler_filter, handler


administration_message_handlers = [
    handle_go_administration()
]
