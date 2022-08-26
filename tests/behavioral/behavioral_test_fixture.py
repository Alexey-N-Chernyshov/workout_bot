import asyncio
import os
from workout_bot.telegram_bot.telegram_bot import TelegramBot
from workout_bot.data_model.statistics import Statistics
from workout_bot.data_model.users import Users
from telegram.ext import CommandHandler, MessageHandler


class TelegramUserMock:
    def __init__(self, user_id, first_name, last_name, username):
        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username


class ChatMock:
    def __init__(self, chat_id):
        self.id = chat_id
        self.type = "private"


class MessageMock:
    def __init__(self, text, from_user, chat):
        self.text = text
        self.from_user = from_user
        self.chat = chat


class UpdateMock:
    def __init__(self, chat, message):
        self.effective_chat = chat
        self.message = message


class ContextTypeMock:
    pass


class BotMock:
    chats = {}

    async def send_message(self, chat_id, text):
        """
        Method is called by the bot, stores text message to compare.
        """

        if chat_id not in self.chats:
            self.chats[chat_id] = []

        self.chats[chat_id].append(text)

    def get_message(self, chat_id):
        if chat_id in self.chats and self.chats[chat_id]:
            return self.chats[chat_id].pop()
        return None


class ApplicationMock:
    bot = BotMock()
    command_handlers = {}

    def add_handler(self, handler):
        if isinstance(handler, CommandHandler):
            command, = handler.commands
            self.command_handlers[command] = handler.callback
        elif isinstance(handler, MessageHandler):
            self.message_handler = handler.callback


class UserMock:
    def __init__(self, application, user_id, first_name, last_name, username):
        self.application = application
        self.bot = application.bot
        self.chat_id = user_id
        self.chat_with_bot = ChatMock(self.chat_id)
        self.user = TelegramUserMock(user_id, first_name, last_name, username)

    def send_message(self, text):
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
        actual = self.bot.get_message(self.chat_id)

        assert actual == expected_text

    def expect_no_more_answers(self):
        actual = self.bot.get_message(self.chat_id)

        assert actual is None


class DataModelMock:
    USERS_STORAGE = "users_storage"
    TABLE_IDS_STORAGE = "table_ids_storage"

    def delete_file(self, filename):
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
        self.delete_file(self.USERS_STORAGE)
        self.delete_file(self.TABLE_IDS_STORAGE)


class BehavioralTest:
    def __init__(self):
        self.application = ApplicationMock()
        self.data_model = DataModelMock()
        self.telegram_bot = TelegramBot(self.application, self.data_model)
        self.user_counter = 1
        self.users = []

    def add_user(self, first_name, last_name, user_name):
        user = UserMock(self.application, self.user_counter, first_name,
                        last_name, user_name)
        self.user_counter += 1
        self.users.append(user)
        return user

    def teardown(self):
        self.data_model.cleanup()
