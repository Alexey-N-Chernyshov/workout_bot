"""
Tests of users views.
"""

from workout_bot.data_model.users import UserContext
from workout_bot.view.users import user_to_text_message
from workout_bot.view.users import user_to_short_text_message


def test_user_to_message():
    """
    Test text representation of user with first name, last name and user name.
    """

    user = UserContext(user_id=42,
                       first_name="Alice",
                       last_name="Liddell",
                       username="wondergirl")

    actual = user_to_text_message(user)
    expected = "@wondergirl \\- Alice Liddell"

    assert actual == expected


def test_user_to_message_only_id():
    """
    Test text representation of user without first name, last name and user
    name.
    """
    user = UserContext(user_id=42)

    actual = user_to_text_message(user)
    expected = "id: 42"

    assert actual == expected


def test_user_to_message_only_username():
    """
    Test text representation of user with only user name.
    """
    user = UserContext(user_id=42,
                       username="wondergirl")

    actual = user_to_text_message(user)
    expected = "@wondergirl"

    assert actual == expected


def test_user_to_message_only_full_name():
    """
    Test text representation of user with only first and last names.
    """
    user = UserContext(user_id=42,
                       first_name="Alice",
                       last_name="Liddell")

    actual = user_to_text_message(user)
    expected = "Alice Liddell, id: 42"

    assert actual == expected


def test_user_to_message_only_first_name():
    """
    Test text representation of user with only first name.
    """

    user = UserContext(user_id=42,
                       first_name="Alice")

    actual = user_to_text_message(user)
    expected = "Alice, id: 42"

    assert actual == expected


def test_user_to_message_only_last_name():
    """
    Test text representation of user with only last names.
    """

    user = UserContext(user_id=42,
                       last_name="Liddell")

    actual = user_to_text_message(user)
    expected = "Liddell, id: 42"

    assert actual == expected


def test_user_to_message_username_and_first_name():
    """
    Test text representation of user with only first and user names.
    """

    user = UserContext(user_id=42,
                       first_name="Alice",
                       username="wondergirl")

    actual = user_to_text_message(user)
    expected = "@wondergirl \\- Alice"

    assert actual == expected


def test_user_to_message_username_and_last_name():
    """
    Test text representation of user with only last and user names.
    """

    user = UserContext(user_id=42,
                       last_name="Liddell",
                       username="wondergirl")

    actual = user_to_text_message(user)
    expected = "@wondergirl \\- Liddell"

    assert actual == expected


def test_user_to_short_message():
    """
    Test short text representation of user with username.
    """

    user = UserContext(user_id=42,
                       first_name="Alice",
                       last_name="Liddell",
                       username="wondergirl")

    actual = user_to_short_text_message(user)
    expected = "@wondergirl"

    assert actual == expected


def test_user_to_short_message_without_username():
    """
    Test text representation of user without username.
    """

    user = UserContext(user_id=42,
                       first_name="Alice",
                       last_name="Liddell")

    actual = user_to_short_text_message(user)
    expected = "id: 42"

    assert actual == expected
