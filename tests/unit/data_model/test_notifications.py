"""
Tests for DataModel.Notifications.
"""

import datetime
from workout_bot.notification import Notification
from workout_bot.data_model.notifications import Notifications


def test_do_not_add_already_added_notification():
    """
    Do not duplicate notifications.
    """

    notifications = Notifications()
    first = Notification("one", "first")
    first.datetime = datetime.date(2022, 8, 1)
    notifications.add(first)

    notifications.add(first)

    assert len(notifications.list()) == 1
    assert notifications.get_last() == first

    second = Notification("one", "first")
    second.datetime = datetime.date(2022, 8, 2)
    notifications.add(second)

    assert len(notifications.list()) == 1
    assert notifications.get_last().datetime == datetime.date(2022, 8, 1)


def test_remove_notification():
    """
    Remove some notification.
    """

    notifications = Notifications()
    first = Notification("one", "first")
    notifications.add(first)
    second = Notification("two", "second")
    notifications.add(second)
    third = Notification("three", "third")
    notifications.add(third)

    notifications.remove(second)

    assert len(notifications.list()) == 2
    assert notifications.get_last() == third


def test_list_sorted_by_datetime():
    """
    listed() returns notifications ordered by time.
    """

    notifications = Notifications()
    first = Notification("one", "first")
    first.datetime = datetime.date(2022, 8, 29)
    notifications.add(first)
    second = Notification("two", "second")
    second.datetime = datetime.date(2022, 8, 1)
    notifications.add(second)
    third = Notification("three", "third")
    third.datetime = datetime.date(2022, 8, 10)
    notifications.add(third)

    sorted_notifications = notifications.list()

    assert sorted_notifications[0] == second
    assert sorted_notifications[1] == third
    assert sorted_notifications[2] == first

    assert notifications.get_last() == first
