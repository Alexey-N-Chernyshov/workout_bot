"""
Tests for DataModel.Errors.
"""

from workout_bot.error import Error
from workout_bot.data_model.errors import Errors


def test_do_not_add_already_added():
    """
    Do not duplicate errors.
    """

    errors = Errors()
    first_error = Error("one", "first error")
    errors.add_error(first_error)

    errors.add_error(first_error)

    assert len(errors.list()) == 1
    assert errors.get_last() == first_error


def test_remove_error():
    """
    Remove some error from Errors.
    """

    errors = Errors()
    first_error = Error("one", "first error")
    errors.add_error(first_error)
    second_error = Error("two", "second error")
    errors.add_error(second_error)
    third_error = Error("three", "third error")
    errors.add_error(third_error)

    errors.remove(second_error)

    assert len(errors.list()) == 2
    assert errors.get_last() == third_error
