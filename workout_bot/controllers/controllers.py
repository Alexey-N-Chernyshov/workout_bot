"""
All controllers for telegram bot interaction.
"""

from dataclasses import dataclass
from .authorization import authorization_handlers
from .user_management import UserManagement
from .administration import administration_message_handlers
from .training_management import training_management_message_handlers
from .table_management import table_management_message_handlers
from .table_management import table_management_query_handlers


@dataclass
class Controllers:
    """
    One place of all controllers used in the bot.
    """

    message_handlers = []
    query_handlers = []

    def __init__(self, bot, data_model):
        self.message_handlers.extend(authorization_handlers)
        self.message_handlers.extend(administration_message_handlers)
        self.message_handlers.extend(training_management_message_handlers)
        self.message_handlers.extend(table_management_message_handlers)
        self.query_handlers.extend(table_management_query_handlers)

        self.user_management = UserManagement(bot, data_model)

    async def handle_message(self, data_model, update, context):
        """
        Calls the first handler that satisfies the filter.
        """

        for handler_filter, handler in self.message_handlers:
            if handler_filter(data_model, update):
                return await handler(data_model, update, context)
        return False

    async def handle_query(self, data_model, update, context):
        """
        Calls the first handler that satisfies the filter.
        """

        for handler_filter, handler in self.query_handlers:
            if handler_filter(data_model, update):
                return await handler(data_model, update, context)
        return False
