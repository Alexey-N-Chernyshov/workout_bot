"""
Test notifications representation.
"""

from dataclasses import dataclass
from workout_bot.view.notifications import get_notifications_button_text


@dataclass
class MockDataModel:

    @dataclass
    class MockNotifications:
        number = 0

        def len(self):
            return self.number

    def __init__(self):
        self.notifications = self.MockNotifications()


def test_notification_button_text_empty():
    """
    Given: Data Model with no notifications
    When: get_notifications_button_text called
    Then: no number returned
    """

    data_model = MockDataModel()

    result = get_notifications_button_text(data_model)

    assert result == "Уведомления"


def test_notification_button_text_some():
    """
    Given: Data Model with 2 notifications
    When: get_notifications_button_text called
    Then: no number returned
    """

    data_model = MockDataModel()
    data_model.notifications.number = 2

    result = get_notifications_button_text(data_model)

    assert result == "Уведомления (2)"
