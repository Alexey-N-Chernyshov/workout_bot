"""
Provides user interaction for table manamegent.
"""

from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from data_model.users import UserAction
from data_model.users import AddTableContext, RemoveTableContext
from view.tables import get_table_message, get_all_tables_message
from google_sheets_feeder.utils import get_table_id_from_link


class TableManagement:
    """
    Provides user interaction for table manamegent.
    """

    def __init__(self, bot, data_model):
        self.bot = bot
        self.data_model = data_model

    def show_table_management_panel(self, chat_id,
                                    text="Управление таблицами"):
        """
        Shows table management panel.
        """

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                       one_time_keyboard=True)
        key_show_tables = KeyboardButton(text="Показать все таблицы")
        keyboard.add(key_show_tables)
        key_remove_table = KeyboardButton(text="Удалить таблицу/страницу")
        key_add_table = KeyboardButton(text="Добавить таблицу/страницу")
        keyboard.row(key_remove_table, key_add_table)
        key_reload_plans = KeyboardButton(text="Прочитать таблицы")
        keyboard.add(key_reload_plans)
        key_administration = KeyboardButton(text="Администрирование")
        keyboard.add(key_administration)
        self.bot.send_message(chat_id, text, reply_markup=keyboard,
                              parse_mode="MarkdownV2")

    def prompt_table_id(self, chat_id):
        """
        Asks user to enter table id.
        """

        self.bot.send_message(chat_id, "Введите ссылку на таблицу")

    def prompt_pages(self, chat_id, user_context, show_table=True):
        """
        Asks user to enter table pages.
        """

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                       one_time_keyboard=True)
        key_done = KeyboardButton(text='Готово')
        keyboard.add(key_done)
        text = "Введите название страницы или нажмите \"Готово\"\n"
        if show_table:
            text += "Текущая таблица:\n"
            text += get_table_message(self.data_model,
                                      user_context.user_input_data.table_id)
        self.bot.send_message(chat_id,
                              text,
                              reply_markup=keyboard,
                              parse_mode="MarkdownV2")

    def handle_message(self, message):
        """
        Handles messages related to table management.
        Returns True if messsage was processed, False otherwise.
        """

        user_context = \
            self.data_model.users.get_user_context(message.from_user.id)
        message_text = message.text.strip().lower()

        if not user_context.administrative_permission:
            self.data_model.users.set_user_action(user_context.user_id,
                                                  UserAction.TRAINING)
            return False

        if user_context.action == UserAction.ADMIN_ADDING_TABLE:
            table_id = get_table_id_from_link(message.text)
            user_context.user_input_data.table_id = table_id
            user_context.action = UserAction.ADMIN_ADDING_PAGES
            self.data_model.users.set_user_context(user_context)
            self.prompt_pages(message.chat.id, user_context, show_table=False)
            return True

        if user_context.action == UserAction.ADMIN_REMOVING_TABLE:
            table_id = get_table_id_from_link(message.text)
            user_context.user_input_data.table_id = table_id
            user_context.action = UserAction.ADMIN_REMOVING_PAGES
            self.data_model.users.set_user_context(user_context)
            self.prompt_pages(message.chat.id, user_context)
            return True

        if user_context.action == UserAction.ADMIN_ADDING_PAGES:
            if message_text == "готово":
                self.data_model \
                    .workout_table_names \
                    .add_table(
                        user_context.user_input_data.table_id,
                        user_context.user_input_data.pages)
                user_context.action = UserAction.ADMIN_TABLE_MANAGEMENT
                user_context.user_input_data = None
                self.data_model.users.set_user_context(user_context)
                self.show_table_management_panel(message.chat.id)
            else:
                user_context.user_input_data.pages.append(message.text)
                self.data_model.users.set_user_context(user_context)
                self.prompt_pages(message.chat.id, user_context)
            return True

        if user_context.action == UserAction.ADMIN_REMOVING_PAGES:
            if message_text == "готово":
                self.data_model \
                    .workout_table_names \
                    .remove_table(
                        user_context.user_input_data.table_id,
                        user_context.user_input_data.pages)
                user_context.action = UserAction.ADMIN_TABLE_MANAGEMENT
                user_context.user_input_data = None
                self.data_model.users.set_user_context(user_context)
                self.show_table_management_panel(message.chat.id)
            else:
                user_context.user_input_data.pages.append(message.text)
                self.data_model.users.set_user_context(user_context)
                self.prompt_pages(message.chat.id, user_context)
            return True

        if message_text == "показать все таблицы":
            text = get_all_tables_message(self.data_model)
            self.show_table_management_panel(message.chat.id, text=text)
            return True

        if (message_text in ("добавить таблицу/страницу", "добавить таблицу",
                             "добавить страницу")):
            user_context.action = UserAction.ADMIN_ADDING_TABLE
            user_context.user_input_data = AddTableContext()
            self.data_model.users.set_user_context(user_context)
            self.prompt_table_id(message.chat.id)
            return True

        if (message_text in ("удалить таблицу/страницу", "удалить таблицу",
                             "удалить страницу")):
            user_context.action = UserAction.ADMIN_REMOVING_TABLE
            user_context.user_input_data = RemoveTableContext()
            self.data_model.users.set_user_context(user_context)
            self.prompt_table_id(message.chat.id)
            return True

        if message_text == "прочитать таблицы":
            text = "Идёт обновление таблиц, может занять несколько секунд."
            self.bot.send_message(message.chat.id, text)
            self.data_model.update_tables()
            self.bot.send_message(message.chat.id, "Таблицы обновлены.")
            self.show_table_management_panel(message.chat.id)
            return True

        if message_text == "администрирование":
            # return to above menu
            return False

        if user_context.action == UserAction.ADMIN_TABLE_MANAGEMENT:
            self.show_table_management_panel(message.chat.id)
            return True

        return False
