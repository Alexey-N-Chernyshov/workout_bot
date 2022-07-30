from workout_bot.data_model.users import Users, UserAction, UserContext


def test_get_users_awaiting_authorization():
    users = Users()
    alice = UserContext(user_id=1, action=UserAction.awaiting_authorization)
    users.set_user_context(alice)
    bob = UserContext(user_id=2, action=UserAction.blocked)
    users.set_user_context(bob)
    charlie = UserContext(user_id=3, action=UserAction.awaiting_authorization)
    users.set_user_context(charlie)

    actual = users.get_users_awaiting_authorization()
    expected = {alice, charlie}

    assert actual == expected
