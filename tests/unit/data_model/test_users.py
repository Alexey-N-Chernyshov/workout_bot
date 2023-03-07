"""
Tests for user data model.
"""

from workout_bot.data_model.users import Users, UserAction, UserContext
from workout_bot.data_model.users import BlockUserContext

STORAGE = "storage"


def test_get_users_awaiting_authorization(tmp_path):
    """
    get_users_awaiting_authorization returns only users with status
    AWAITING_AUTHORIZATION
    """

    storage_path = str(tmp_path / STORAGE)
    users = Users(storage_path)
    alice = UserContext(user_id=1, action=UserAction.AWAITING_AUTHORIZATION)
    users.set_user_context(alice)
    bob = UserContext(user_id=2, action=UserAction.BLOCKED)
    users.set_user_context(bob)
    charlie = UserContext(user_id=3, action=UserAction.AWAITING_AUTHORIZATION)
    users.set_user_context(charlie)

    actual = users.get_users_awaiting_authorization()
    expected = {alice, charlie}

    assert actual == expected


def test_user_context_persistent_storage(tmp_path):
    """
    Users data model provides persistent storage.
    """

    storage_path = str(tmp_path / STORAGE)
    users = Users(storage_path)

    user_id = 42
    user_context = UserContext(user_id)
    users.set_user_context(user_context)
    users.set_user_input_data(user_id, BlockUserContext(42))
    assert users.is_present(user_id)
    actual = users.get_user_context(user_id)
    assert actual.user_id == user_id
    assert isinstance(actual.user_input_data, BlockUserContext)
    assert actual.user_input_data.user_id == user_id

    del users
    del actual
    del user_context

    # load again
    users = Users(storage_path)
    assert users.is_present(user_id)
    actual = users.get_user_context(user_id)
    assert actual.user_id == user_id
    assert isinstance(actual.user_input_data, BlockUserContext)
    assert actual.user_input_data.user_id == user_id


def test_get_user_context_by_short_username(tmp_path):
    """
    Short username that starts with "id: xxx" must return user id.
    """

    storage_path = str(tmp_path / STORAGE)
    users = Users(storage_path)
    user_id = 42
    user_context = UserContext(user_id)
    user_context.first_name = "first"
    user_context.last_name = "last"
    user_context.username = None
    users.set_user_context(user_context)

    short_username = f"id: {user_id}"
    actual = users.get_user_context_by_short_username(short_username)
    assert actual.user_id == user_context.user_id
    assert actual.first_name == user_context.first_name
    assert actual.last_name == user_context.last_name
    assert actual.username == user_context.username


def test_get_user_context_by_short_wrong_username(tmp_path):
    """
    Short username malformed must return None.
    """

    storage_path = str(tmp_path / STORAGE)
    users = Users(storage_path)

    assert users.get_user_context_by_short_username("wrong_prefix") is None
    assert users.get_user_context_by_short_username("id: not_a_num") is None
