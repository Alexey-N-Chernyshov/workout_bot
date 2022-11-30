"""
Stores application statistics.
"""

from datetime import datetime


class Statistics:
    """
    Stores application statistics.
    """

    total_requests = 0
    total_commands = 0
    training_time_update_time = datetime.min

    def record_request(self):
        """
        Records request was handled.
        """

        self.total_requests += 1

    def get_total_requests(self):
        """
        Returnds total number of requests handled.
        """

        return self.total_requests

    def record_command(self):
        """
        Records command was handled.
        """

        self.total_commands += 1

    def get_total_commands(self):
        """
        Returns total number of command called.
        """
        return self.total_commands

    def set_training_plan_update_time(self):
        """
        Records time when training plan was updated.
        """

        self.training_time_update_time = datetime.now()

    def get_training_plan_update_time(self):
        """
        Returns time when training plan was updated.
        """

        return self.training_time_update_time
