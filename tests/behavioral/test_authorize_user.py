import os
from workout_bot.telegram_bot.telegram_bot import TelegramBot
from workout_bot.data_model.statistics import Statistics
from workout_bot.data_model.users import Users


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


class TelebotMock:
    chats = {}

    def message_handler(self, commands=[], content_types=[]):
        def decorator(handler):
            if "start" in commands:
                self.start_command_handler = handler
            if "system_stats" in commands:
                self.system_stats_command_handler = handler
            if "text" in content_types:
                self.message_handler = handler

            def inner(message):
                return handler(message)

            return inner

        return decorator

    def send_message(self, chat_id, text):
        """
        Method is called by the bot, store text message to compare.
        """

        if chat_id not in self.chats:
            self.chats[chat_id] = []

        self.chats[chat_id].append(text)

    def get_message(self, chat_id):
        if chat_id in self.chats and self.chats[chat_id]:
            return self.chats[chat_id].pop()
        return None


class UserMock:
    def __init__(self, bot, user_id, first_name, last_name, username):
        self.bot = bot
        self.chat_id = user_id
        self.chat_with_bot = ChatMock(self.chat_id)
        self.user = TelegramUserMock(user_id, first_name, last_name, username)

    def send_message(self, text):
        message = MessageMock(text, self.user, self.chat_with_bot)

        if text == "/start":
            self.bot.start_command_handler(message)
        elif text == "/system_stats":
            self.bot.system_stats_command_handler(message)
        else:
            self.bot.message_handler(message)

    def expect_answer(self, expected_text):
        actual = self.bot.get_message(self.chat_id)

        assert actual == expected_text

    def expect_no_more_answers(self):
        actual = self.bot.get_message(self.chat_id)

        assert actual is None


class DataModelMock:
    USERS_STORAGE = "users_storage"
    TABLE_IDS_STORAGE = "table_ids_storage"

    def __init__(self):
        try:
            os.remove(self.USERS_STORAGE)
            os.remove(self.TABLE_IDS_STORAGE)
        except OSError:
            pass

        self.statistics = Statistics()
        self.users = Users(self.USERS_STORAGE)


class BehavioralTest:
    def __init__(self):
        self.bot = TelebotMock()
        self.data_model = DataModelMock()
        self.telegram_bot = TelegramBot(self.bot, self.data_model)
        self.alice = UserMock(self.bot, 11, "Alice", "Liddell", "wondergirl")


def test_authorization():
    test = BehavioralTest()

    test.alice.send_message("/start")
    test.alice.expect_answer("Ожидайте подтверждения авторизации")
    test.alice.expect_no_more_answers()

    assert True
