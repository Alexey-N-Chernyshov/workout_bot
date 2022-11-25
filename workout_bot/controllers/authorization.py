"""
Provides user interaction for authorization process.
"""


def handle_blocked():
    """
    Shows blocking message for blocked users.
    """

    def handler_filter(data_model, update):
        return data_model.users.is_user_blocked(update.message.from_user.id)

    async def handler(_data_model, update, context):
        await context.bot.send_message(update.effective_chat.id,
                                       "Вы заблокированы.")
        return True

    return handler_filter, handler


def handle_unauthorized():
    """
    Asks unathorized users wait for authorization.
    """

    def handler_filter(data_model, update):
        return data_model.users \
            .is_user_awaiting_authorization(update.message.from_user.id)

    async def handler(_data_model, update, context):
        await context.bot.send_message(update.effective_chat.id,
                                       "Ожидайте подтверждения авторизации")
        return True

    return handler_filter, handler


authorization_handlers = [handle_blocked(), handle_unauthorized()]
