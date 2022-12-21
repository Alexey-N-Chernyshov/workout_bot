"""
Authorization messages handlers.
"""


def handle_blocked():
    """
    Shows blocking message for blocked users.
    """

    def handler_filter(data_model, update):
        """
        Checks if user is blocked.
        """

        return data_model.users.is_user_blocked(update.message.from_user.id)

    async def handler(_data_model, update, context):
        """
        Shows user is blocked message.
        """

        await context.bot.send_message(
            update.effective_chat.id,
            "Вы заблокированы."
        )

    return handler_filter, handler


def handle_unauthorized():
    """
    Asks unathorized users wait for authorization.
    """

    def handler_filter(data_model, update):
        """
        Checks if user unauthorized.
        """

        return data_model.users \
            .is_user_awaiting_authorization(update.message.from_user.id)

    async def handler(_data_model, update, context):
        await context.bot.send_message(
            update.effective_chat.id,
            "Ожидайте подтверждения авторизации"
        )

    return handler_filter, handler


authorization_handlers = [handle_blocked(), handle_unauthorized()]
