"""
Provides user interaction for authorization process.
"""

from telegram import Update


class Authorization:
    """
    Prvides user interaction methods for authorization.
    """

    def __init__(self, bot, data_model):
        self.bot = bot
        self.data_model = data_model

    async def handle_message(self, update: Update):
        """
        Handles text messages from user.
        """

        user_id = update.message.from_user.id
        chat_id = update.effective_chat.id

        if self.data_model.users.is_user_blocked(user_id):
            await self.bot.send_message(chat_id, "Вы заблокированы.")
            return True

        if self.data_model.users.is_user_awaiting_authorization(user_id):
            await self.bot.send_message(chat_id,
                                        "Ожидайте подтверждения авторизации")
            return True

        return False
