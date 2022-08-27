"""
Tests for user data model.
"""

from workout_bot.data_model.users import Users, UserAction, UserContext
from workout_bot.data_model.users import AddTableContext
from .utils import delete_file

STORAGE = "storage"


def test_get_users_awaiting_authorization():
    """
    get_users_awaiting_authorization returns only users with status
    AWAITING_AUTHORIZATION
    """

    users = Users(STORAGE)
    alice = UserContext(user_id=1, action=UserAction.AWAITING_AUTHORIZATION)
    users.set_user_context(alice)
    bob = UserContext(user_id=2, action=UserAction.BLOCKED)
    users.set_user_context(bob)
    charlie = UserContext(user_id=3, action=UserAction.AWAITING_AUTHORIZATION)
    users.set_user_context(charlie)

    actual = users.get_users_awaiting_authorization()
    expected = {alice, charlie}

    assert actual == expected


def test_user_context_persistent_storage():
    """
    Users data model provides persistent storage.
    """

    delete_file(STORAGE)

    users = Users(STORAGE)

    user_id = 42
    user_context = UserContext(user_id)
    user_context.user_input_data = AddTableContext("table_id",
                                                   ["page1", "page2"])
    users.set_user_context(user_context)
    actual = users.get_user_context(user_id)
    assert actual.user_id == user_id
    assert isinstance(actual.user_input_data, AddTableContext)
    assert actual.user_input_data.table_id == "table_id"
    assert len(actual.user_input_data.pages) == 2
    assert "page1" in actual.user_input_data.pages
    assert "page2" in actual.user_input_data.pages

    del users
    del actual
    del user_context

    # load again
    users = Users(STORAGE)
    actual = users.get_user_context(user_id)
    assert actual.user_id == user_id
    assert isinstance(actual.user_input_data, AddTableContext)
    assert actual.user_input_data.table_id == "table_id"
    assert len(actual.user_input_data.pages) == 2
    assert "page1" in actual.user_input_data.pages
    assert "page2" in actual.user_input_data.pages

    delete_file(STORAGE)
