"""
Provides user interaction for table manamegent.
"""

from telegram import Update
from telegram import KeyboardButton, ReplyKeyboardMarkup
from data_model.users import UserAction
from data_model.users import AddTableContext, RemoveTableContext
from view.tables import get_table_message, get_all_tables_message
from google_sheets_feeder.utils import get_table_id_from_link


async def send_with_table_management_panel(bot, chat_id,
                                           text="Управление таблицами"):
    """
    Shows table management panel.
    """

    keyboard = [
        [KeyboardButton("Показать все таблицы")],
        [
            KeyboardButton("Удалить таблицу/страницу"),
            KeyboardButton("Добавить таблицу/страницу")
        ],
        [KeyboardButton("Прочитать таблицы")],
        [KeyboardButton("Администрирование")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await bot.send_message(chat_id, text, reply_markup=reply_markup,
                           parse_mode="MarkdownV2")


def handle_show_tables():
    """
    Handles switch to training status.
    """

    def handler_filter(data_model, update):
        """
        Admin wants do display all tables.
        """

        user_id = update.message.from_user.id
        user_context = data_model.users.get_user_context(user_id)
        message_text = update.message.text.strip().lower()
        return (user_context.action == UserAction.ADMIN_TABLE_MANAGEMENT
                and message_text == "показать все таблицы")

    async def handler(data_model, update, context):
        """
        Shows all tables.
        """

        user_id = update.message.from_user.id
        user_context = data_model.users.get_user_context(user_id)
        chat_id = user_context.chat_id
        print("handler")
        print(chat_id)
        text = get_all_tables_message(data_model)
        await send_with_table_management_panel(context.bot, chat_id, text=text)
        return True

    return (handler_filter, handler)

table_management_message_handlers = [
    handle_show_tables()
]

class TableManagement:
    """
    Provides user interaction for table manamegent.
    """

    def __init__(self, bot, data_model):
        self.bot = bot
        self.data_model = data_model

    async def show_table_management_panel(self, chat_id,
                                          text="Управление таблицами"):
        """
        Shows table management panel.
        """

        keyboard = [
            [KeyboardButton("Показать все таблицы")],
            [
                KeyboardButton("Удалить таблицу/страницу"),
                KeyboardButton("Добавить таблицу/страницу")
            ],
            [KeyboardButton("Прочитать таблицы")],
            [KeyboardButton("Администрирование")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await self.bot.send_message(chat_id, text, reply_markup=reply_markup,
                                    parse_mode="MarkdownV2")

    async def prompt_table_id(self, chat_id):
        """
        Asks user to enter table id.
        """

        await self.bot.send_message(chat_id, "Введите ссылку на таблицу")

    async def prompt_pages(self, chat_id, user_context, show_table=True):
        """
        Asks user to enter table pages.
        """

        text = "Введите название страницы или нажмите \"Готово\"\n"
        if show_table:
            text += "Текущая таблица:\n"
            text += get_table_message(self.data_model,
                                      user_context.user_input_data.table_id)

        keyboard = [[KeyboardButton("Готово")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await self.bot.send_message(chat_id, text, reply_markup=reply_markup,
                                    parse_mode="MarkdownV2")

    async def handle_message(self, update: Update):
        """
        Handles messages related to table management.
        Returns True if messsage was processed, False otherwise.
        """

        chat_id = update.effective_chat.id
        user_context = \
            self.data_model.users.get_user_context(update.message.from_user.id)
        message_text = update.message.text.strip().lower()

        if user_context.action == UserAction.ADMIN_ADDING_TABLE:
            table_id = get_table_id_from_link(update.message.text)
            user_context.user_input_data.table_id = table_id
            user_context.action = UserAction.ADMIN_ADDING_PAGES
            self.data_model.users.set_user_context(user_context)
            await self.prompt_pages(chat_id, user_context,
                                    show_table=False)
            return True

        if user_context.action == UserAction.ADMIN_REMOVING_TABLE:
            table_id = get_table_id_from_link(update.message.text)
            user_context.user_input_data.table_id = table_id
            user_context.action = UserAction.ADMIN_REMOVING_PAGES
            self.data_model.users.set_user_context(user_context)
            await self.prompt_pages(chat_id, user_context)
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
                await self.show_table_management_panel(chat_id)
            else:
                user_context.user_input_data.pages.append(update.message.text)
                self.data_model.users.set_user_context(user_context)
                self.prompt_pages(chat_id, user_context)
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
                await self.show_table_management_panel(chat_id)
            else:
                user_context.user_input_data.pages.append(update.message.text)
                self.data_model.users.set_user_context(user_context)
                await self.prompt_pages(chat_id, user_context)
            return True

        if (message_text in ("добавить таблицу/страницу", "добавить таблицу",
                             "добавить страницу")):
            user_context.action = UserAction.ADMIN_ADDING_TABLE
            user_context.user_input_data = AddTableContext()
            self.data_model.users.set_user_context(user_context)
            await self.prompt_table_id(chat_id)
            return True

        if (message_text in ("удалить таблицу/страницу", "удалить таблицу",
                             "удалить страницу")):
            user_context.action = UserAction.ADMIN_REMOVING_TABLE
            user_context.user_input_data = RemoveTableContext()
            self.data_model.users.set_user_context(user_context)
            await self.prompt_table_id(chat_id)
            return True

        if message_text == "прочитать таблицы":
            text = "Идёт обновление таблиц, может занять несколько секунд."
            await self.bot.send_message(chat_id, text)
            self.data_model.update_tables()
            await self.bot.send_message(chat_id, "Таблицы обновлены.")
            await self.show_table_management_panel(chat_id)
            return True

        if message_text == "администрирование":
            # return to above menu
            return False

        if user_context.action == UserAction.ADMIN_TABLE_MANAGEMENT:
            await self.show_table_management_panel(chat_id)
            return True

        return False
