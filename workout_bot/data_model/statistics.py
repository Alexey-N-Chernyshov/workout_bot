from datetime import datetime

class Statistics:
    total_requests = 0
    total_commands = 0
    training_time_update_time = datetime.min

    def record_request(self):
        self.total_requests += 1

    def get_total_requests(self):
        return self.total_requests

    def record_command(self):
        self.total_commands += 1

    def get_total_commands(self):
        return self.total_commands

    def set_training_plan_update_time(self):
        self.training_time_update_time = datetime.now()

    def get_training_plan_update_time(self):
        return self.training_time_update_time
