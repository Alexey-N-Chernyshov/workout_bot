"""
Stores errors in temporary memory.
"""


class Errors:
    """
    Stores application errors to show to admins.
    """

    def __init__(self):
        self.__errors = []

    def add_error(self, error):
        """
        Adds error to the storage.
        """

        if error not in self.__errors:
            self.__errors.append(error)

    def remove(self, error):
        """
        Removes error from the storage.
        id - error UUID
        """

        self.__errors.remove(error)

    def list(self):
        """
        Returns all the errors.
        """

        return self.__errors

    def get_last(self):
        """
        Returns the most recent error.
        """

        return self.__errors[-1]
