"""
Storage of excercises names and links.
"""

SHELVE_KEY_TABLE_ID = "table_id"
SHELVE_KEY_PAGENAME = "pagename"


class ExcerciseLinks:
    """
    Provides access to excercise links.
    """

    def __init__(self, table_id, pagename, feeder):
        """
        Sets shelve storage filename.
        """
        self.table_id = table_id
        self.pagename = pagename
        self.feeder = feeder

    def load_excercise_links(self):
        """
        Loads excercise links from google table.
        """
        self.excercise_links = self.feeder.load_excercise_links(self.table_id,
                                                                self.pagename)

    def get_excercise_links(self):
        """
        Returns loaded excercise links.
        """
        return self.excercise_links
