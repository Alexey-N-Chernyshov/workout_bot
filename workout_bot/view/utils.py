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
