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

        self.__errors.append(error)

    def remove_error(self, error_id):
        """
        Removes error from the storage.
        id - error UUID
        """

        return list(filter(
            lambda err: err.error_id != error_id, self.__errors
        ))

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
