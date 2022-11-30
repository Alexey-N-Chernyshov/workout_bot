"""
Storage of exercises names and links.
"""

SHELVE_KEY_TABLE_ID = "table_id"
SHELVE_KEY_PAGENAME = "pagename"


class ExerciseLinks:
    """
    Provides access to exercise links.
    """

    def __init__(self, table_id, pagename, feeder):
        """
        Sets shelve storage filename.
        """
        self.table_id = table_id
        self.pagename = pagename
        self.feeder = feeder
        self.exercise_links = {}

    def update_exercise_links(self):
        """
        Loads exercise links from Google table.
        """

        self.exercise_links = self.feeder.get_exercise_links(self.table_id,
                                                             self.pagename)

    def get_exercise_links(self):
        """
        Returns loaded exercise links.
        """

        return self.exercise_links
