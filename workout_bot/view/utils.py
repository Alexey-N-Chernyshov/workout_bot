"""
Helper functions for representation.
"""


def ireplace(text, old, new):
    """
    Replace case-insensitive
    """

    if old.lower() in text.lower():
        index_l = text.lower().index(old.lower())
        return text[:index_l] + new + text[index_l + len(old):]
    return text


def escape_text(text):
    """
    Escape text for MarkdownV2
    """
    text = text.replace('\\', '\\\\')
    text = text.replace('(', '\\(')
    text = text.replace(')', '\\)')
    text = text.replace('-', '\\-')
    text = text.replace('+', '\\+')
    text = text.replace('.', '\\.')
    text = text.replace('=', '\\=')
    text = text.replace('_', '\\_')
    text = text.replace('!', '\\!')
    return text
