"""
Behavioral tests for user management.
"""

from workout_bot.data_model.users import (
    AssignTableUserContext, BlockUserContext, UserAction
)
from workout_bot.view.utils import escape_text


async def test_go_user_management(test_user_management):
    """
    Given: admin in ADMINISTRATION state.
    When: admin sends go to user management.
    Then: admin is in ADMIN_USER_MANAGEMENT state and user management panel is
    sent.
    """

    admin = test_user_management.admin
    admin.set_user_action(UserAction.ADMINISTRATION)

    await admin.send_message("Управление пользователями")

    expected = "Управление пользователями"
    admin.expect_answer(expected)
    admin.expect_no_more_answers()
    admin.assert_user_action(UserAction.ADMIN_USER_MANAGEMENT)


async def test_show_all_users(test_user_management):
    """
    Given: admin in ADMIN_USER_MANAGEMENT state.
    When: admin sends show all users message.
    Then: admin is shown all users.
    """

    admin = test_user_management.admin

    await admin.send_message("Показать всех")

    table = escape_text(test_user_management.workout_table.table_name)
    expected = "Ожидают авторизации:\n"
    expected += " \\- @waiting\n"
    expected += "\n"
    expected += "Тренируются:\n"
    expected += f" \\- @admin \\- *администратор* \\- {table} \\- неделя: 0\n"
    expected += f" \\- @user \\- {table} \\- неделя: 0\n"
    expected += "\n"
    expected += "Заблокрироанные:\n"
    expected += " \\- @blocked\n"
    admin.expect_answer(expected)
    admin.expect_no_more_answers()


async def test_go_authorize_user(test_user_management):
    """
    Given: Admin is in ADMIN_USER_MANAGEMENT state.
    When: Admin sends message for user authorization.
    Then: Admin is in ADMIN_USER_AUTHORIZATION state.
    """

    admin = test_user_management.admin
    admin.set_user_action(UserAction.ADMIN_USER_MANAGEMENT)

    await admin.send_message("Авторизация пользователей")

    expected = "Ожидают авторизации:\n"
    expected += " \\- @waiting\n"
    admin.expect_answer(expected)
    admin.expect_no_more_answers()
    admin.assert_user_action(UserAction.ADMIN_USER_AUTHORIZATION)


async def test_go_authorize_user_no_users(test_user_management):
    """
    Given: Admin is in ADMIN_USER_MANAGEMENT state and there is no users
    awaiting authorization.
    When: Admin sends message for user authorization.
    Then: Admin is in ADMIN_USER_MANAGEMENT state.
    """

    admin = test_user_management.admin
    admin.set_user_action(UserAction.ADMIN_USER_MANAGEMENT)
    no_more_waiting = test_user_management.waiting
    no_more_waiting.set_user_action(UserAction.TRAINING)

    await admin.send_message("Авторизация пользователей")

    admin.expect_answer("Никто не ждёт авторизации")
    admin.expect_no_more_answers()
    admin.assert_user_action(UserAction.ADMIN_USER_MANAGEMENT)


async def test_authorize_user(test_user_management):
    """
    Given: Admin is in ADMIN_USER_AUTHORIZATION state and user in
    AWAITING_AUTHORIZATION state.
    When: admin sends message to authorize user.
    Then: user in AWAITING_AUTHORIZATION state, admin in
    ADMIN_USER_ASSIGNING_TABLE state.
    """

    admin = test_user_management.admin
    admin.set_user_action(UserAction.ADMIN_USER_AUTHORIZATION)
    waiting = test_user_management.waiting
    table = test_user_management.workout_table.table_name

    await admin.send_message("Авторизовать @waiting")

    expected = "Какую таблицу назначим для @waiting?\n\n"
    expected += f" \\- {escape_text(table)}\n"
    admin.expect_answer(expected)
    admin.expect_no_more_answers()
    admin.assert_user_action(UserAction.ADMIN_USER_ASSIGNING_TABLE)
    waiting.assert_user_action(UserAction.AWAITING_AUTHORIZATION)


async def test_authorize_wrong_user(test_user_management):
    """
    Given: Admin is in ADMIN_USER_AUTHORIZATION state.
    When: admin sends message with wrong username.
    Then: admin in ADMIN_USER_AUTHORIZATION state.
    """

    admin = test_user_management.admin
    admin.set_user_action(UserAction.ADMIN_USER_AUTHORIZATION)

    await admin.send_message("Авторизовать @wrong_username")

    admin.expect_answer("Нет такого пользователя")
    admin.expect_answer("Управление пользователями")
    admin.expect_no_more_answers()
    admin.assert_user_action(UserAction.ADMIN_USER_AUTHORIZATION)


async def test_assign_user_table(test_user_management):
    """
    Given: Admin is in ADMIN_USER_ASSIGNING_TABLE state and user in
    AWAITING_AUTHORIZATION state.
    When: admin sends message to assign a table for the user.
    Then: user in CHOOSING_PLAN state, admin in ADMIN_USER_MANAGEMENT state.
    """

    admin = test_user_management.admin
    admin.set_user_action(UserAction.ADMIN_USER_ASSIGNING_TABLE)
    waiting = test_user_management.waiting
    admin.set_user_data(AssignTableUserContext(waiting.user.id))
    table_name = test_user_management.workout_table.table_name
    table_id = test_user_management.workout_table.table_id

    await admin.send_message(table_name)

    # admin
    admin.expect_answer("Управление пользователями")
    admin.expect_no_more_answers()
    admin.assert_user_action(UserAction.ADMIN_USER_MANAGEMENT)
    # user is notified
    expected = f"Назначена программа тренировок *{escape_text(table_name)}*\n"
    expected += "\n"
    expected += "Для продолжения нажмите \"Перейти к тренировкам\""
    waiting.expect_answer(expected)
    admin.expect_no_more_answers()
    waiting.assert_user_action(UserAction.CHOOSING_PLAN)
    assert waiting.get_user_context().current_table_id == table_id


async def test_assign_user_wrong_table(test_user_management):
    """
    Given: Admin is in ADMIN_USER_ASSIGNING_TABLE state and user in
    AWAITING_AUTHORIZATION state.
    When: admin sends message to assign a table for the user with wrong table
     name.
    Then: user in AWAITING_AUTHORIZATION state, admin in
    ADMIN_USER_ASSIGNING_TABLE state.
    """

    admin = test_user_management.admin
    admin.set_user_action(UserAction.ADMIN_USER_ASSIGNING_TABLE)
    waiting = test_user_management.waiting
    admin.set_user_data(AssignTableUserContext(waiting.user.id))
    table_name = test_user_management.workout_table.table_name

    wrong_table = "wrong table name"
    await admin.send_message(wrong_table)

    expected = f"Нет таблицы с именем '{wrong_table}'.\n"
    expected += "Какую таблицу назначим для @waiting?\n\n"
    expected += f" \\- {escape_text(table_name)}\n"
    admin.expect_answer(expected)
    admin.expect_no_more_answers()
    admin.assert_user_action(UserAction.ADMIN_USER_ASSIGNING_TABLE)
    waiting.assert_user_action(UserAction.AWAITING_AUTHORIZATION)


async def test_block_user(test_user_management):
    """
    Given: Admin is in ADMIN_USER_AUTHORIZATION state and user in
    AWAITING_AUTHORIZATION state.
    When: admin sends message to block user.
    Then: user in AWAITING_AUTHORIZATION state, admin in ADMIN_USER_BLOCKING
    state and block confirmation is shown.
    """

    admin = test_user_management.admin
    admin.set_user_action(UserAction.ADMIN_USER_AUTHORIZATION)
    waiting = test_user_management.waiting

    await admin.send_message("Блокировать @waiting")

    expected = "Заблокировать пользователя @waiting?"
    admin.expect_answer(expected)
    admin.expect_no_more_answers()
    admin.assert_user_action(UserAction.ADMIN_USER_BLOCKING)
    waiting.assert_user_action(UserAction.AWAITING_AUTHORIZATION)


async def test_block_wrong_user(test_user_management):
    """
    Given: Admin is in ADMIN_USER_AUTHORIZATION state and user in
    AWAITING_AUTHORIZATION state.
    When: admin sends message to block user with wrong username.
    Then: user in AWAITING_AUTHORIZATION state, admin in ADMIN_USER_BLOCKING
    state and block confirmation is shown.
    """

    admin = test_user_management.admin
    admin.set_user_action(UserAction.ADMIN_USER_AUTHORIZATION)
    waiting = test_user_management.waiting

    await admin.send_message("Блокировать @wrong_username")

    admin.expect_answer("Нет такого пользователя")
    admin.expect_answer("Управление пользователями")
    admin.expect_no_more_answers()
    admin.assert_user_action(UserAction.ADMIN_USER_AUTHORIZATION)
    waiting.assert_user_action(UserAction.AWAITING_AUTHORIZATION)


async def test_confirm_user_block(test_user_management):
    """
    Given: Admin is in ADMIN_USER_BLOCKING state.
    When: admin sends confirm blocking.
    Then: user is blocked, admin is in ADMIN_USER_MANAGEMENT state.
    """

    admin = test_user_management.admin
    admin.set_user_action(UserAction.ADMIN_USER_BLOCKING)
    user = test_user_management.user
    admin.set_user_data(BlockUserContext(user.user.id))

    await admin.send_message("Да")

    expected = f"@{user.user.username} заблокирован."
    admin.expect_answer(expected)
    admin.expect_answer("Управление пользователями")
    admin.expect_no_more_answers()
    admin.assert_user_action(UserAction.ADMIN_USER_MANAGEMENT)
    user.assert_user_action(UserAction.BLOCKED)


async def test_cancel_user_block(test_user_management):
    """
    Given: Admin is in ADMIN_USER_BLOCKING state.
    When: admin sends cancel blocking.
    Then: user is not blocked, admin is in ADMIN_USER_MANAGEMENT state.
    """

    admin = test_user_management.admin
    admin.set_user_action(UserAction.ADMIN_USER_BLOCKING)
    user = test_user_management.user
    admin.set_user_data(BlockUserContext(user.user.id))

    await admin.send_message("Нет")

    admin.expect_answer("Управление пользователями")
    admin.expect_no_more_answers()
    admin.assert_user_action(UserAction.ADMIN_USER_MANAGEMENT)
    user.assert_user_action(UserAction.TRAINING)


async def test_unrecognized_user_block(test_user_management):
    """
    Given: Admin is in ADMIN_USER_BLOCKING state.
    When: admin sends unrecognized message.
    Then: user is not blocked, admin is in ADMIN_USER_BLOCKING state.
    """

    admin = test_user_management.admin
    admin.set_user_action(UserAction.ADMIN_USER_BLOCKING)
    user = test_user_management.user
    admin.set_user_data(BlockUserContext(user.user.id))

    await admin.send_message("nor yes nor no")

    expected = "Заблокировать пользователя @user?"
    admin.expect_answer(expected)
    admin.expect_no_more_answers()
    admin.assert_user_action(UserAction.ADMIN_USER_BLOCKING)
    user.assert_user_action(UserAction.TRAINING)


async def test_go_add_admin(test_user_management):
    """
    Given: Admin is in ADMIN_USER_MANAGEMENT state.
    When: Admin sends message for admin adding.
    Then: Admin is in ADMIN_ADDING_ADMIN state.
    """

    admin = test_user_management.admin
    admin.set_user_action(UserAction.ADMIN_USER_MANAGEMENT)

    await admin.send_message("Добавить администратора")

    expected = "Кому дать права администратора?\n"
    expected += " \\- @waiting\n"
    expected += " \\- @user\n"
    admin.expect_answer(expected)
    admin.expect_no_more_answers()
    admin.assert_user_action(UserAction.ADMIN_ADDING_ADMIN)


async def test_go_add_admin_no_one(test_with_workout_tables):
    """
    Given: Admin is in ADMIN_USER_MANAGEMENT state.
    When: Admin sends message for admin adding.
    Then: Admin is in ADMIN_ADDING_ADMIN state.
    """

    test = test_with_workout_tables
    admin = test.add_admin(user_name="admin")
    admin.set_user_action(UserAction.ADMIN_USER_MANAGEMENT)

    await admin.send_message("Добавить администратора")

    admin.expect_answer("Некого назначить администратором")
    admin.expect_no_more_answers()
    admin.assert_user_action(UserAction.ADMIN_USER_MANAGEMENT)


async def test_add_admin(test_user_management):
    """
    Given: Admin is in ADMIN_ADDING_ADMIN state and user has no
    administrative permission.
    When: admin sends message to promote the user to admin.
    Then: admin in ADMIN_USER_MANAGEMENT state and user has
    administrative permission.
    """

    admin = test_user_management.admin
    admin.set_user_action(UserAction.ADMIN_ADDING_ADMIN)
    user = test_user_management.user

    await admin.send_message("@user")

    admin.expect_answer("Управление пользователями")
    admin.expect_no_more_answers()
    assert user.get_user_context().administrative_permission


async def test_add_admin_wrong_name(test_user_management):
    """
    Given: Admin is in ADMIN_ADDING_ADMIN state and user has no administrative
    permission.
    When: admin sends message to promote the user to admin with wrong username.
    Then: admin in ADMIN_USER_MANAGEMENT state and user has administrative
    permission.
    """

    admin = test_user_management.admin
    admin.set_user_action(UserAction.ADMIN_ADDING_ADMIN)
    user = test_user_management.user

    await admin.send_message("@wrong_username")

    admin.expect_answer("Нет такого пользователя")
    admin.expect_no_more_answers()
    admin.assert_user_action(UserAction.ADMIN_USER_MANAGEMENT)

    assert not user.get_user_context().administrative_permission
