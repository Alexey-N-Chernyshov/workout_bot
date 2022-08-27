"""
Infrastructure and mocks for behavioral tests.
"""

import asyncio
import os
from dataclasses import dataclass
from telegram.ext import CommandHandler, MessageHandler
from workout_bot.telegram_bot.telegram_bot import TelegramBot
from workout_bot.data_model.statistics import Statistics
from workout_bot.data_model.users import Users


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

    def __init__(self, text, from_user, chat):
        self.text = text
        self.from_user = from_user
        self.chat = chat


@dataclass
class UpdateMock:
    """
    Class used by python-telegram-bot to notify the bot.
    """

    def __init__(self, chat, message):
        self.effective_chat = chat
        self.message = message


@dataclass
class ContextTypeMock:
    """
    Class used by python-telegram-bot.
    """


class BotMock:
    """
    Telegram bot mock.
    """

    chats = {}

    async def send_message(self, chat_id, text):
        """
        Method is called by the bot, stores text message to compare.
        """

        if chat_id not in self.chats:
            self.chats[chat_id] = []

        self.chats[chat_id].append(text)

    def get_message(self, chat_id):
        """
        Returns a message sent by the bot in the chat with chat_id.
        """
        if chat_id in self.chats and self.chats[chat_id]:
            return self.chats[chat_id].pop()
        return None


class ApplicationMock:
    """
    Python-telegram-bot application mock is used for handler registration.
    """

    bot = BotMock()
    command_handlers = {}
    message_handler = None

    def add_handler(self, handler):
        """
        Adds handler for python-telegram-bot
        """

        if isinstance(handler, CommandHandler):
            command, = handler.commands
            self.command_handlers[command] = handler.callback
        elif isinstance(handler, MessageHandler):
            self.message_handler = handler.callback

    def run_polling(self):
        """
        Mock for polling.
        """


class UserMock:
    """
    Represents the user interaction with the bot.
    """

    # pylint: disable=too-many-arguments
    def __init__(self, application, user_id, first_name, last_name, username):
        self.application = application
        self.bot = application.bot
        self.chat_id = user_id
        self.chat_with_bot = ChatMock(self.chat_id)
        self.user = TelegramUserMock(user_id, first_name, last_name, username)

    def send_message(self, text):
        """
        The user sends message to the bot private chat.
        """

        message = MessageMock(text, self.user, self.chat_with_bot)
        update = UpdateMock(self.chat_with_bot, message)
        context = ContextTypeMock()

        async def async_send():
            if text.startswith('/'):
                await self.application \
                    .command_handlers[text[1:]](update, context)
            else:
                await self.application.message_handler(update, context)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(async_send())
        loop.close()

    def expect_answer(self, expected_text):
        """
        The user expects answer from the bot.
        """

        actual = self.bot.get_message(self.chat_id)

        assert actual == expected_text

    def expect_no_more_answers(self):
        """
        Ensures there is no more messages from the bot.
        """

        actual = self.bot.get_message(self.chat_id)

        assert actual is None


class DataModelMock:
    """
    Data model used for the bot.
    """

    USERS_STORAGE = "users_storage"
    TABLE_IDS_STORAGE = "table_ids_storage"

    def delete_file(self, filename):
        """
        Helper function to delete a file.
        """

        try:
            os.remove(filename)
        except OSError:
            pass

    def __init__(self):
        self.delete_file(self.USERS_STORAGE)
        self.delete_file(self.TABLE_IDS_STORAGE)

        self.statistics = Statistics()
        self.users = Users(self.USERS_STORAGE)

    def cleanup(self):
        """
        Cleans up when the class is not needed anymore.
        """

        self.delete_file(self.USERS_STORAGE)
        self.delete_file(self.TABLE_IDS_STORAGE)


class BehavioralTest:
    """
    All infrastructure for test in one place.
    """

    def __init__(self):
        self.application = ApplicationMock()
        self.data_model = DataModelMock()
        self.telegram_bot = TelegramBot(self.application, self.data_model)
        self.user_counter = 1
        self.users = []

    def add_user(self, first_name, last_name, user_name):
        """
        Adds user to the test and returns UserMock.
        """

        user = UserMock(self.application, self.user_counter, first_name,
                        last_name, user_name)
        self.user_counter += 1
        self.users.append(user)
        return user

    def teardown(self):
        """
        Tear down the fixture.
        """

        self.data_model.cleanup()
