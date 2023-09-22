"""
Representations for data model notifications.
"""


def get_notifications_button_text(data_model):
    """
    Returns following text:
    - "Уведомления" if number of notifications is 0;
    - "Уведомления (N)" if number of notifications is N > 0.
    """

    result = "Уведомления"
    number = data_model.notifications.len()
    if number > 0:
        result += " (" + str(number) + ")"
    return result
