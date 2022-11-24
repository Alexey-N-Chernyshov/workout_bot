"""
Provides user interaction for table manamegent.
"""

from telegram import Update
from telegram import KeyboardButton, ReplyKeyboardMarkup
from data_model.users import UserAction
from data_model.users import AddTableContext, RemoveTableContext
from view.tables import get_table_message, get_all_tables_message
from google_sheets_feeder.utils import get_table_id_from_link
from telegram_bot.utils import get_user_context


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


def handle_go_table_management():
    """
    Handles switch to training status.
    """

    def handler_filter(data_model, update):
        """
        The user wants go to table management.
        """

        user_context = get_user_context(data_model, update)
        message_text = update.message.text.strip().lower()
        return (user_context.administrative_permission and
                user_context.action in (UserAction.TRAINING,
                                        UserAction.ADMINISTRATION,
                                        UserAction.ADMIN_TABLE_MANAGEMENT)
                and message_text == "управление таблицами")

    async def handler(data_model, update, context):
        """
        Show table management panel and switch state.
        """

        user_context = get_user_context(data_model, update)
        data_model.users.set_user_action(user_context.user_id,
                                         UserAction.ADMIN_TABLE_MANAGEMENT)
        await send_with_table_management_panel(context.bot,
                                               update.effective_chat.id)
        return True

    return (handler_filter, handler)


def handle_show_tables():
    """
    Handles show all tables.
    """

    def handler_filter(data_model, update):
        """
        Admin wants do display all tables.
        """

        user_context = get_user_context(data_model, update)
        message_text = update.message.text.strip().lower()
        return (user_context.action == UserAction.ADMIN_TABLE_MANAGEMENT
                and message_text == "показать все таблицы")

    async def handler(data_model, update, context):
        """
        Shows all tables.
        """

        user_context = get_user_context(data_model, update)
        chat_id = user_context.chat_id
        text = get_all_tables_message(data_model)
        await send_with_table_management_panel(context.bot, chat_id, text=text)
        return True

    return (handler_filter, handler)


def handle_add_table():
    """
    Handles add table/page.
    """

    def handler_filter(data_model, update):
        """
        Admin wants do add table or page.
        """

        user_context = get_user_context(data_model, update)
        message_text = update.message.text.strip().lower()
        return (user_context.action == UserAction.ADMIN_TABLE_MANAGEMENT
                and message_text in (("добавить таблицу/страницу",
                                      "добавить таблицу",
                                      "добавить страницу")))

    async def handler(data_model, update, context):
        """
        Shows all tables.
        """

        user_context = get_user_context(data_model, update)
        chat_id = user_context.chat_id

        data_model.users.set_user_action(user_context.user_id,
                                         UserAction.ADMIN_ADDING_TABLE)
        data_model.users.set_user_input_data(user_context.user_id,
                                             AddTableContext())
        await context.bot.send_message(chat_id, "Введите ссылку на таблицу")

######
        # #TODO ask table name, pass loader, handle error
        # loader = GoogleSheetsLoader()
        # pages = loader.get_sheet_names("1x2DpoqS9lxUNNWKf5hp4VhHWblWZm-mTTu5I5L3jhtw")
        #
        # keyboard = []
        # for page in pages:
        #     keyboard.append([InlineKeyboardButton(page, callback_data=page)])
        # reply_markup = InlineKeyboardMarkup(keyboard, resize_keyboard=True)
        #
        # await context.bot.send_message(chat_id, "*table name*",
        #                                reply_markup=reply_markup,
        #                                parse_mode="MarkdownV2")

        # await send_with_table_management_panel(context.bot, chat_id, "Added")
        return True

    return (handler_filter, handler)


def handle_update_tables():
    """
    Handles update tables request.
    """

    def handler_filter(data_model, update):
        """
        Admin wants do update all tables.
        """

        user_context = get_user_context(data_model, update)
        message_text = update.message.text.strip().lower()
        return (user_context.action == UserAction.ADMIN_TABLE_MANAGEMENT
                and message_text == "прочитать таблицы")

    async def handler(data_model, update, context):
        """
        Updates all tables.
        """

        user_context = get_user_context(data_model, update)
        chat_id = user_context.chat_id
        text = "Идёт обновление таблиц, может занять несколько секунд"
        await context.bot.send_message(chat_id, text)
        data_model.update_tables()
        await context.bot.send_message(chat_id, "Таблицы обновлены")
        await send_with_table_management_panel(context.bot, chat_id)
        return True

    return (handler_filter, handler)


def handle_other_messages():
    """
    Handles other messages.
    """

    def handler_filter(data_model, update):
        """
        Admin in ADMIN_TABLE_MANAGEMENT state.
        """

        user_context = get_user_context(data_model, update)
        return user_context.action == UserAction.ADMIN_TABLE_MANAGEMENT

    async def handler(data_model, update, context):
        """
        Handle other messages.
        """

        user_context = get_user_context(data_model, update)
        chat_id = user_context.chat_id
        await send_with_table_management_panel(context.bot, chat_id)
        return True

    return (handler_filter, handler)


table_management_message_handlers = [
    handle_go_table_management(),
    handle_show_tables(),
    handle_add_table(),
    handle_update_tables(),
    handle_other_messages()
]


class TableManagement:
    """
    Provides user interaction for table manamegent.
    """

    def __init__(self, bot, data_model):
        self.bot = bot
        self.data_model = data_model

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
                await send_with_table_management_panel(self.bot, chat_id)
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
                await send_with_table_management_panel(self.bot, chat_id)
            else:
                user_context.user_input_data.pages.append(update.message.text)
                self.data_model.users.set_user_context(user_context)
                await self.prompt_pages(chat_id, user_context)
            return True

        if (message_text in ("удалить таблицу/страницу", "удалить таблицу",
                             "удалить страницу")):
            user_context.action = UserAction.ADMIN_REMOVING_TABLE
            user_context.user_input_data = RemoveTableContext()
            self.data_model.users.set_user_context(user_context)
            await self.prompt_table_id(chat_id)
            return True

        return False
