"""
Provides access to workout table ids and pages that need to be loaded.
"""

import shelve


class WorkoutTableNames:
    """
    Stores google table ids and pages with workouts to be loaded.
    """

    __storage_filename = ""

    # Table ids and page names to read
    # {google_spreadsheet_id: [page names]}
    __workout_tables = {}

    def __init__(self, filename):
        """
        Sets shelve storage filename.
        """

        self.__storage_filename = filename
        self.__workout_tables = shelve.open(self.__storage_filename,
                                            writeback=True)

    def is_table_present(self, table_id):
        """
        Checks if table_id is present.
        """

        if table_id is None:
            return False
        return table_id in self.__workout_tables

    def add_table(self, table_id, pages):
        """
        Adds table pages to the table with talbe_id. If table_id is not
        present, creates the new one.
        """

        pages = set(pages)
        if pages:
            if table_id in self.__workout_tables:
                self.__workout_tables[table_id].update(pages)
                self.__workout_tables.sync()
            else:
                self.__workout_tables[table_id] = pages
                self.__workout_tables.sync()

    def remove_table(self, table_id, pages):
        """
        Deletes table pages from the table with talbe_id. If table with
        table_id has no pages, deletes the table.
        """

        if table_id in self.__workout_tables:
            self.__workout_tables[table_id].difference_update(pages)
            self.__workout_tables.sync()
            if not self.__workout_tables[table_id]:
                self.__workout_tables.pop(table_id, None)
                self.__workout_tables.sync()

    def switch_pages(self, table_id, page):
        """
        Adds page if the page is not present. If page is present, removes it.
        """

        if table_id in self.__workout_tables:
            if page in self.__workout_tables[table_id]:
                self.__workout_tables[table_id].remove(page)
            else:
                self.__workout_tables[table_id].add(page)
        else:
            self.__workout_tables[table_id] = {page}

    def get_tables(self):
        """
        Returns all the tables.
        """

        return self.__workout_tables

    def is_plan_present(self, table_id, plan):
        """
        Checks if table with table_id has page named plan.
        """

        if table_id is None or plan is None:
            return False
        return plan in self.get_plan_names(table_id)

    def get_plan_names(self, table_id):
        """
        Returns all plans for a table with table_id.
        """

        return self.__workout_tables.get(table_id, [])
