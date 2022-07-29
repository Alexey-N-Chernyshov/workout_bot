def get_table_id_from_link(link):
    prefix = "https://docs.google.com/spreadsheets/d/"
    if link.startswith(prefix):
        rest = link[len(prefix):]
        if '/' in rest:
            return rest.split('/', 1)[0]
    return None
