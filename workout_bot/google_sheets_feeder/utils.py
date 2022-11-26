"""
Helper funstions for google tables.
"""


def get_table_id_from_link(link):
    """
    Extracts table_id from link to google table.
    Returns table_id as str or None if link is malformed.
    """

    prefix = "https://docs.google.com/spreadsheets/d/"
    if link.startswith(prefix):
        rest = link[len(prefix):]
        if '/' in rest:
            return rest.split('/', 1)[0]
        return rest
    return None
