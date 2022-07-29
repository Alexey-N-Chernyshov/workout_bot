from data_model.users import UserAction


class Authentication:
    def __init__(self, bot, data_model):
        self.bot = bot
        self.data_model = data_model

    def handle_message(self, message):
        user_context = \
            self.data_model.users.get_user_context(message.from_user.id)

        if not user_context:
            text = "Вы не авторизованы.\n"
            text += "Нажмите на команду /start для начала авторизации."
            self.bot.send_message(message.chat.id, text)
            return True

        # waiting for specific input
        if user_context.action == UserAction.awaiting_authz:
            self.bot.send_message(message.chat.id,
                                  "Ожидайте подтверждения авторизации")
            return True
