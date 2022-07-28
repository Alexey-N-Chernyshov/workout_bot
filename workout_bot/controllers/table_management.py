from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from data_model.users import UserAction
from data_model.users import AddTableContext, RemoveTableContext
from view.tables import get_table_message, get_all_tables_message

class TableManagement:
    def __init__(self, bot, data_model):
        self.bot = bot
        self.data_model = data_model

    def show_table_management_panel(self, chat_id, user_context,
                                    text="Управление таблицами"):
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
        text = "Введите идентификатор таблицы.\n\n" + \
            "Идентификатор может быть найден в ссылке на таблицу (spreadsheetId):\n" + \
            "<code>https://docs.google.com/spreadsheets/d/</code><b><u>spreadsheetId</u></b><code>/edit#gid=0</code>"
        self.bot.send_message(chat_id, text, parse_mode="HTML")

    def prompt_pages(self, chat_id, user_context, show_table=True):
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
            user_context.action = UserAction.training
            return False

        if user_context.action == UserAction.admin_adding_table:
            user_context.user_input_data.table_id = message.text
            user_context.action = UserAction.admin_adding_pages
            self.prompt_pages(message.chat.id, user_context, show_table=False)
            return True

        if user_context.action == UserAction.admin_removing_table:
            user_context.user_input_data.table_id = message.text
            user_context.action = UserAction.admin_removing_pages
            self.prompt_pages(message.chat.id, user_context)
            return True

        if user_context.action == UserAction.admin_adding_pages:
            if message_text == "готово":
                self.data_model \
                    .add_table(
                        user_context.user_input_data.table_id,
                        user_context.user_input_data.pages)
                user_context.action = UserAction.administration
                user_context.user_input_data = None
                self.show_table_management_panel(message.chat.id, user_context)
            else:
                user_context.user_input_data.pages.append(message.text)
                self.prompt_pages(message.chat.id, user_context)
            return True

        if user_context.action == UserAction.admin_removing_pages:
            if message_text == "готово":
                self.data_model \
                    .remove_table(
                        user_context.user_input_data.table_id,
                        user_context.user_input_data.pages)
                user_context.action = UserAction.administration
                user_context.user_input_data = None
                self.show_table_management_panel(message.chat.id, user_context)
            else:
                user_context.user_input_data.pages.append(message.text)
                self.prompt_pages(message.chat.id, user_context)
            return True

        if message_text == "показать все таблицы":
            text = get_all_tables_message(self.data_model)
            self.show_table_management_panel(message.chat.id, user_context,
                                             text=text)
            return True

        if (message_text == "добавить таблицу/страницу"
            or message_text == "добавить таблицу"
            or message_text == "добавить страницу"):
            user_context.action = UserAction.admin_adding_table
            user_context.user_input_data = AddTableContext()
            self.prompt_table_id(message.chat.id)
            return True

        if (message_text == "удалить таблицу/страницу"
            or message_text == "удалить таблицу"
            or message_text == "удалить страницу"):
            user_context.action = UserAction.admin_removing_table
            user_context.user_input_data = RemoveTableContext()
            self.prompt_table_id(message.chat.id)
            return True

        if message_text == "прочитать таблицы":
            self.bot.send_message(message.chat.id,
                                  "Идёт обновление таблиц, может занять несколько секунд.")
            self.data_model.update_tables()
            self.bot.send_message(message.chat.id, "Таблицы обновлены.")
            self.show_table_management_panel(message.chat.id, user_context)
            return True

        if message_text == "администрирование":
            # will be handled above
            return False

        if user_context.action == UserAction.admin_table_management:
            self.show_table_management_panel(message.chat.id, user_context)
            return True

        return False
