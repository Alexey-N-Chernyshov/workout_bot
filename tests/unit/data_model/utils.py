import os


def delete_file(filename):
    try:
        os.remove(filename)
    except OSError:
        pass
