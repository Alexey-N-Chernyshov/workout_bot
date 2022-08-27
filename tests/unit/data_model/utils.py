"""
Helpers for data model tests.
"""

import os


def delete_file(filename):
    """
    Deletes file.
    """

    try:
        os.remove(filename)
    except OSError:
        pass
