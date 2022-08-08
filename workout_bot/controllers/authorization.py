"""
Provides user interaction for authorization process.
"""

from data_model.users import UserAction


class Authorization:
    """
    Prvides user interaction methods for authorization.
    """

    def __init__(self, bot, data_model):
        self.bot = bot
        self.data_model = data_model

    def handle_message(self, message):
        """
        Handles text messages from user.
        """

        user_id = message.from_user.id
        user_context = self.data_model.users.get_user_context(user_id)

        if user_context is None:
            text = "Вы не авторизованы.\n"
            text += "Нажмите /start"
            self.bot.send_message(message.chat.id, text)
            return True

        if user_context.action == UserAction.BLOCKED:
            self.bot.send_message(message.chat.id, "Вы заблокированы.")
            return True

        if self.data_model.users.is_user_awaiting_authorization(user_id):
            self.bot.send_message(message.chat.id,
                                  "Ожидайте подтверждения авторизации")
            return True

        return False
