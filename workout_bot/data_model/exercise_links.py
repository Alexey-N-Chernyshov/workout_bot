"""
Storage of exercises names and links.
"""


class ExerciseLinks:
    """
    Provides access to exercise links.
    """

    def __init__(self, page_reference, feeder):
        """
        Sets shelve storage filename.
        """
        self.page_reference = page_reference
        self.feeder = feeder
        self.exercise_links = {}

    def update_exercise_links(self):
        """
        Loads exercise links from Google table.
        """

        self.exercise_links = self.feeder.get_exercise_links(
            self.page_reference
        )

    def get_exercise_links(self):
        """
        Returns loaded exercise links.
        """

        return self.exercise_links
