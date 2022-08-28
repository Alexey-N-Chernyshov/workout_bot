"""
All controllers for telegram bot interaction.
"""

from dataclasses import dataclass
from .authorization import authorization_handlers
from .administration import Administration
from .table_management import TableManagement
from .user_management import UserManagement
from .training_management import TrainingManagement


@dataclass
class Controllers:
    """
    One place of all controllers used in the bot.
    """

    handlers = []

    def __init__(self, bot, data_model):
        self.handlers.extend(authorization_handlers)
        self.administration = Administration(bot, data_model)
        self.user_management = UserManagement(bot, data_model)
        self.table_management = TableManagement(bot, data_model)
        self.training_management = TrainingManagement(bot, data_model)

    async def handle(self, data_model, update, context):
        """
        Calls the first handler that satisfies the filter.
        """

        for handler_filter, handler in self.handlers:
            if handler_filter(data_model, update):
                return await handler(data_model, update, context)
        return False
