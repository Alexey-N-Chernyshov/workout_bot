"""
All controllers for telegram bot interaction.
"""

from .administration import Administration
from .authorization import Authorization
from .table_management import TableManagement
from .user_management import UserManagement
from .training_management import TrainingManagement


class Controllers:
    """
    One place of all controllers used in the bot.
    """

    def __init__(self, bot, data_model):
        self.administration = Administration(bot, data_model)
        self.authorization = Authorization(bot, data_model)
        self.user_management = UserManagement(bot, data_model)
        self.table_management = TableManagement(bot, data_model)
        self.training_management = TrainingManagement(bot, data_model)
