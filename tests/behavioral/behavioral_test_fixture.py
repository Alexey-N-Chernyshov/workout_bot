"""
Infrastructure and mocks for behavioral tests.
"""

from dataclasses import dataclass
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
from workout_bot.telegram_bot.telegram_bot import TelegramBot
from workout_bot.data_model.users import UserAction
from workout_bot.data_model.data_model import DataModel, PageReference
from workout_bot.view.workouts import get_workout_text_message


@dataclass
class TelegramUserMock:
    """
    Telegram User mock with unique id and name.
    """

    def __init__(self, user_id, first_name, last_name, username):
        # pylint: disable=invalid-name
        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username


@dataclass
class ChatMock:
    """
    Telegram chat mock.
    """

    def __init__(self, chat_id):
        # pylint: disable=invalid-name
        self.id = chat_id
        self.type = "private"


@dataclass
class MessageMock:
    """
    Telegram message mock.
    """

    def __init__(self, text, from_user):
        self.text = text
        self.from_user = from_user


@dataclass
class QueryMock:
    """
    Telegram inline query mock.
    """

    def __init__(self, data, from_user):
        self.data = data
        self.from_user = from_user
        self.message = MessageMock("", from_user)

    async def edit_message_text(self, text, reply_markup):
        """
        Mock for Query.edit_message_text.
        """

    async def answer(self):
        """
        Querry callback is answered.
        """


@dataclass
class UpdateMock:
    """
    Class used by python-telegram-bot to notify the bot.
    """

    def __init__(self, chat, message=None, query=None):
        self.effective_chat = chat
        if message:
            self.message = message
        if query:
            self.callback_query = query


@dataclass
class ContextTypeMock:
    """
    Class used by python-telegram-bot.
    """

    def __init__(self, bot):
        self.bot = bot


class BotMock:
    """
    Telegram bot mock.
    """

    def __init__(self):
        self.chats = {}

    # pylint: disable=too-many-arguments
    async def send_message(self, chat_id, text,
                           parse_mode=None,
                           disable_web_page_preview=False,
                           disable_notification=False,
                           reply_markup=None):
        """
        Method is called by the bot, stores text message to compare.
        """

        _ = parse_mode
        _ = disable_web_page_preview
        _ = disable_notification
        _ = reply_markup

        if chat_id not in self.chats:
            self.chats[chat_id] = []

        self.chats[chat_id].append(text)

    def get_message(self, chat_id):
        """
        Returns a message sent by the bot in the chat with chat_id.
        """

        if chat_id in self.chats and self.chats[chat_id]:
            return self.chats[chat_id].pop(0)
        return None


class ApplicationMock:
    """
    Python-telegram-bot application mock is used for handler registration.
    """

    def __init__(self):
        self.bot = BotMock()
        self.command_handlers = {}
        self.message_handler = None
        self.query_handler = None

    def add_handler(self, handler):
        """
        Adds handler for python-telegram-bot
        """

        if isinstance(handler, CommandHandler):
            command, = handler.commands
            self.command_handlers[command] = handler.callback
        elif isinstance(handler, MessageHandler):
            self.message_handler = handler.callback
        elif isinstance(handler, CallbackQueryHandler):
            self.query_handler = handler.callback

    def run_polling(self):
        """
        Mock for polling.
        """


@dataclass
class LoaderMock:
    """
    Mock for Google spreadsheets loader.
    """

    def __init__(self):
        self.page_names = []

    def get_sheet_names(self, _spreadsheet_id):
        """
        Loads page names.
        """

        return self.page_names


class UserMock:
    """
    Represents the user interaction with the bot.
    """

    def __init__(self, application, data_model, chat_id, telegram_user):
        self.application = application
        self.data_model = data_model
        self.bot = application.bot
        self.chat_with_bot = ChatMock(chat_id)
        self.user = telegram_user

    def set_user_action(self, action):
        """
        Sets state for the user.
        """

        self.data_model.users.set_user_action(self.user.id, action)

    def set_table(self, table_id):
        """
        Sets table id for the user.
        """

        self.data_model.users.set_table_for_user(self.user.id, table_id)

    def set_page(self, page):
        """
        Sets page for the user.
        """

        self.data_model.users.set_page_for_user(self.user.id, page)

    def set_week_number(self, week):
        """
        Sets week number for the user.
        """

        user_context = self.data_model.users.get_user_context(self.user.id)
        user_context.current_week = week
        self.data_model.users.set_user_context(user_context)

    def set_workout_number(self, workout):
        """
        Sets workout number for the user.
        """

        user_context = self.data_model.users.get_user_context(self.user.id)
        user_context.current_workout = workout
        self.data_model.users.set_user_context(user_context)

    def set_user_data(self, data):
        """
        Sets user context input data.
        """

        self.data_model.users.set_user_input_data(self.user.id, data)

    def get_user_context(self):
        """
        Returns data model user context.
        """

        return self.data_model.users.get_user_context(self.user.id)

    async def send_message(self, text):
        """
        The user sends message to the bot private chat.
        """

        message = MessageMock(text, self.user)
        update = UpdateMock(self.chat_with_bot, message=message)
        context = ContextTypeMock(self.bot)

        if text.startswith('/'):
            await self.application \
                .command_handlers[text[1:]](update, context)
        else:
            await self.application.message_handler(update, context)

    async def press_inline_button(self, text, data):
        """
        The user taps inline button with data.
        text - replied message text
        data - attached to reply button data
        """
        query = QueryMock(data, self.user)
        query.message.text = text
        update = UpdateMock(self.chat_with_bot, query=query)
        context = ContextTypeMock(self.bot)
        await self.application.query_handler(update, context)

    def expect_answer(self, expected_text):
        """
        The user expects answer from the bot.
        """

        actual = self.bot.get_message(self.chat_with_bot.id)
        if actual != expected_text:
            print("Actual:")
            print(actual)
            print("Expected:")
            print(expected_text)

        assert actual == expected_text

    def expect_no_more_answers(self):
        """
        Ensures there is no more messages from the bot.
        """

        actual = self.bot.get_message(self.chat_with_bot.id)
        if actual:
            print(actual)

        assert actual is None

    def assert_user_action(self, expected_action):
        """
        Asserts that user action is expected one in data model.
        """

        actual_action = self.data_model \
            .users.get_user_context(self.user.id).action

        assert actual_action == expected_action


class DataModelMock(DataModel):
    """
    Data model used for the bot.
    """

    USERS_STORAGE = "users_storage"
    TABLE_IDS_STORAGE = "table_ids_storage"

    def __init__(self, tmp_path):
        self.updated = False

        super().__init__(
            str(tmp_path / self.USERS_STORAGE),
            str(tmp_path / self.TABLE_IDS_STORAGE),
            PageReference(
                "exercise_links_table_id",
                "exercise_links_pagename",
            )
        )

    def update_tables(self):
        """
        Updates tables mock.
        """

        self.updated = True


# pylint: disable=too-many-instance-attributes
class BehavioralTest:
    """
    All infrastructure for test in one place.
    """

    def __init__(self, tmp_path):
        self.application = ApplicationMock()
        self.data_model = DataModelMock(tmp_path)
        self.loader = LoaderMock()
        self.telegram_bot = TelegramBot(
            self.application,
            self.loader,
            self.data_model,
            "behavioral_test"
        )
        self.user_counter = 1
        self.users = []
        self.workout_tables = []

    def add_user(self, first_name="", last_name="", user_name=""):
        """
        Adds user to the test and returns UserMock.
        """

        telegram_user = TelegramUserMock(self.user_counter, first_name,
                                         last_name, user_name)
        user = UserMock(self.application, self.data_model, self.user_counter,
                        telegram_user)
        self.user_counter += 1
        self.users.append(user)
        return user

    def add_user_context(self,
                         first_name="",
                         last_name="",
                         user_name="",
                         action=UserAction.CHOOSING_PLAN):
        """
        Adds user to data_model.
        """

        user = self.add_user(first_name, last_name, user_name)

        user_context = self.data_model \
            .users.get_or_create_user_context(user.user.id)
        user_context.user_id = user.user.id
        user_context.first_name = user.user.first_name
        user_context.last_name = user.user.last_name
        user_context.username = user.user.username
        user_context.chat_id = user.user.id
        user_context.current_page = None
        user_context.current_week = 0
        user_context.current_workout = 0
        user_context.action = action
        self.data_model.users.set_user_context(user_context)

        return user

    def add_admin(self, first_name="", last_name="", user_name=""):
        """
        Adds user with administrative permissions.
        """

        user = self.add_user_context(first_name, last_name, user_name)
        self.data_model.users.set_administrative_permission(user.user.id)
        self.data_model.users.set_user_action(user.user.id,
                                              UserAction.CHOOSING_PLAN)
        return user

    def get_choose_plan_message(self, table):
        """
        Returns message from choose plan prompt.
        """

        plans = self.data_model.workout_table_names.get_plan_names(
            table.table_id
        )
        text = "Выберите программу из списка:\n"
        for plan in plans:
            text += f"\n - {plan}"
        return text

    def add_table(self, table):
        """
        Adds workout table plans for test suite.
        """

        self.workout_tables.append(table)
        self.data_model.workout_plans.update_workout_table(table)
        self.data_model.workout_table_names.add_table(table.table_id,
                                                      table.pages.keys())

    def get_expected_workout_text_message(self, user):
        """
        Returns expected text message for current workout
        """

        user_context = self.data_model.users.get_user_context(user.user.id)
        return get_workout_text_message(
            self.data_model,
            user_context.current_table_id,
            user_context.current_page,
            user_context.current_week,
            user_context.current_workout
        )
