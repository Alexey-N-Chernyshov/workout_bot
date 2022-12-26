"""
Prints Google table values and cell merges for tests.
"""

import sys
from workout_bot.google_sheets_feeder.google_sheets_loader import (
    GoogleSheetsLoader
)


def main():
    """
    Displays Google tables data.
    """

    table_id = sys.argv[1]
    page_name = sys.argv[2]

    loader = GoogleSheetsLoader()
    name, merges, values = loader.get_values_and_merges(table_id, page_name)
    print(name)
    print(merges)
    print(values)


if __name__ == "__main__":
    main()
