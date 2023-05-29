"""
Stores notifications in temporary memory.
"""


class Notifications:
    """
    Stores application notifications to show to admins.
    """

    def __init__(self):
        self.__notifications = set()

    def add(self, notification):
        """
        Adds notification to the storage.
        """

        if notification not in self.__notifications:
            self.__notifications.add(notification)

    def remove(self, notification):
        """
        Removes notification from the storage.
        """

        self.__notifications.discard(notification)

    def len(self):
        """
        Returns the number of notifications.
        """

        return len(self.__notifications)

    def list(self):
        """
        Returns all the notifications, ordered by date.
        """

        def by_datetime(notification):
            return notification.datetime

        return sorted(self.__notifications, key=by_datetime)

    def get_last(self):
        """
        Returns the most recent notification.
        """

        return self.list()[-1]
