"""
Provides user interaction for table manamegent.
"""

from telegram import (
    KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton,
    InlineKeyboardMarkup
)
from data_model.users import UserAction
from view.tables import get_all_tables_message, get_table_name_message
from view.utils import escape_text
from google_sheets_feeder.utils import get_table_id_from_link
from telegram_bot.utils import get_user_context


class TableManagementController:
    """
    Table management handlers
    """

    def __init__(self, loader):
        self.loader = loader

    def message_handlers(self):
        """
        Returns message handlers.
        """

        return [
            self.handle_go_table_management(),
            self.handle_show_tables(),
            self.handle_add_table(),
            self.handle_cancel_add_table(),
            self.handle_add_table_pages(),
            self.handle_change_table(),
            self.handle_update_tables(),
            self.handle_other_messages()
        ]

    def query_handlers(self):
        """
        Returns InlineKeyboard handlers.
        """

        return [
            self.query_handler_add_page(),
            self.query_handler_change_table()
        ]

    QUERY_ACTION_SWITCH_PAGE = 's'
    QUERY_ACTION_CHOOSE_TABLE = 't'

    class InlineKeyboardData:
        """
        Compact InlineKeyboard encoding.
        First character of string is an InlineKeyboardAction.
        Rest is a data.
        """

        def __init__(self, action, data):
            self.action = action
            self.data = data

        def encode(self):
            """
            Encodes self to string.
            """
            return str(self.action) + self.data

        @staticmethod
        def decode(encoded):
            """
            Decodes InlineKeyboardData from string.
            """
            return TableManagementController.InlineKeyboardData(
                encoded[0],
                encoded[1:]
            )

    @staticmethod
    async def send_with_table_management_panel(bot, chat_id,
                                               text="Управление таблицами"):
        """
        Shows table management panel.
        """

        keyboard = [
            [KeyboardButton("Показать все таблицы")],
            [
                KeyboardButton("Добавить таблицу"),
                KeyboardButton("Изменить таблицу")
            ],
            [KeyboardButton("Прочитать таблицы")],
            [KeyboardButton("Администрирование")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await bot.send_message(chat_id, text, reply_markup=reply_markup,
                               parse_mode="MarkdownV2")

    def inline_keyboard_table_pages(self, data_model, table_id):
        """
        Builds InlineKeyboard with all pages in table.
        """

        pages = self.loader.get_sheet_names(table_id)
        pages_present = data_model.workout_table_names.get_plan_names(table_id)
        keyboard = []
        if pages:
            for page in pages:
                if page in pages_present:
                    page_text = "✅ " + page
                else:
                    page_text = "⏺ " + page
                data = TableManagementController.InlineKeyboardData(
                    TableManagementController.QUERY_ACTION_SWITCH_PAGE,
                    page
                )
                keyboard.append(
                    [InlineKeyboardButton(
                        page_text, callback_data=data.encode())]
                )
        return InlineKeyboardMarkup(keyboard)

    def handle_go_table_management(self):
        """
        Handles switch to table management.
        """

        def handler_filter(data_model, update):
            """
            The admin wants go to table management.
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
            Shows table management panel and switch state.
            """

            user_context = get_user_context(data_model, update)
            data_model.users.set_user_action(user_context.user_id,
                                             UserAction.ADMIN_TABLE_MANAGEMENT)
            await TableManagementController.send_with_table_management_panel(
                context.bot,
                update.effective_chat.id
            )
            return True

        return handler_filter, handler

    def handle_show_tables(self):
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
            await TableManagementController.send_with_table_management_panel(
                context.bot,
                chat_id,
                text=text
            )
            return True

        return handler_filter, handler

    def handle_add_table(self):
        """
        Handles add table/page.
        """

        def handler_filter(data_model, update):
            """
            Admin wants to add table or page.
            """

            user_context = get_user_context(data_model, update)
            message_text = update.message.text.strip().lower()
            return (user_context.administrative_permission and
                    user_context.action == UserAction.ADMIN_TABLE_MANAGEMENT
                    and message_text == ("добавить таблицу"))

        async def handler(data_model, update, context):
            """
            Shows all tables.
            """

            user_context = get_user_context(data_model, update)
            chat_id = user_context.chat_id

            data_model.users.set_user_action(user_context.user_id,
                                             UserAction.ADMIN_ADDING_TABLE)

            keyboard = [[KeyboardButton("Отмена")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await context.bot.send_message(chat_id,
                                           "Введите ссылку на таблицу",
                                           reply_markup=reply_markup)

        return handler_filter, handler

    def handle_cancel_add_table(self):
        """
        Handles cancel message when adding table prompt is active.
        """

        def handler_filter(data_model, update):
            """
            User is in ADMIN_ADDING_TABLE and sent Cancel message.
            """

            user_context = get_user_context(data_model, update)
            message_text = update.message.text.strip().lower()
            return (user_context.action == UserAction.ADMIN_ADDING_TABLE
                    and message_text == ("отмена"))

        async def handler(data_model, update, context):
            """
            Changes user status to ADMIN_TABLE_MANAGEMENT.
            """

            user_context = get_user_context(data_model, update)
            chat_id = user_context.chat_id

            data_model.users.set_user_action(user_context.user_id,
                                             UserAction.ADMIN_TABLE_MANAGEMENT)
            await TableManagementController.send_with_table_management_panel(
                context.bot,
                chat_id
            )

        return handler_filter, handler

    def handle_add_table_pages(self):
        """
        Handles table link submission by admin.
        """

        def handler_filter(data_model, update):
            """
            Admin is in ADMIN_ADDING_TABLE and has sent table id.
            """

            user_context = get_user_context(data_model, update)
            return user_context.action == UserAction.ADMIN_ADDING_TABLE

        async def handler(data_model, update, context):
            """
            Tries to load table and shows `Add table pages` message with inline
            keyboard.
            """

            user_context = get_user_context(data_model, update)
            chat_id = user_context.chat_id
            table_id = get_table_id_from_link(update.message.text)

            try:
                table_name = data_model.workout_plans.get_plan_name(table_id)
                text = "Добавление таблицы\n"
                text += get_table_name_message(table_name, table_id)
                text += "id: " + escape_text(table_id) + "\n"
                text += "\n"
                text += "Отметьте страницы с тренировками"
                reply_markup = self.inline_keyboard_table_pages(
                    data_model, table_id)
                await context.bot.send_message(chat_id, text,
                                               reply_markup=reply_markup,
                                               parse_mode="MarkdownV2")
                data_model \
                    .users.set_user_action(user_context.user_id,
                                           UserAction.ADMIN_TABLE_MANAGEMENT)
                await TableManagementController \
                    .send_with_table_management_panel(context.bot,
                                                      update.effective_chat.id)
            except (AttributeError, TypeError):
                text = "Ошибка при загрузке таблицы"
                await context.bot.send_message(chat_id, text)
                keyboard = [[KeyboardButton("Отмена")], ]
                reply_markup = ReplyKeyboardMarkup(
                    keyboard, resize_keyboard=True)
                await context.bot.send_message(chat_id,
                                               "Введите ссылку на таблицу",
                                               reply_markup=reply_markup)

            return True

        return handler_filter, handler

    def handle_change_table(self):
        """
        Handles change table that already has been added.
        """

        def handler_filter(data_model, update):
            """
            Admin sent change table message.
            """

            user_context = get_user_context(data_model, update)
            message_text = update.message.text.strip().lower()
            return (user_context.administrative_permission and
                    user_context.action == UserAction.ADMIN_TABLE_MANAGEMENT
                    and message_text == "изменить таблицу")

        async def handler(data_model, update, context):
            """
            Asks what table to change.
            """

            user_context = get_user_context(data_model, update)
            chat_id = user_context.chat_id

            keyboard = []
            table_ids = data_model.workout_table_names.get_tables().keys()
            for table_id in table_ids:
                table_name = data_model.workout_plans.get_plan_name(table_id)
                if table_name is None:
                    table_name = "id: " + table_id
                data = TableManagementController.InlineKeyboardData(
                    TableManagementController.QUERY_ACTION_CHOOSE_TABLE,
                    table_id
                )
                keyboard.append(
                    [InlineKeyboardButton(
                        table_name, callback_data=data.encode())]
                )
            keyboard = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id,
                "Выберите таблицу для редактирования",
                reply_markup=keyboard
            )

        return handler_filter, handler

    def handle_update_tables(self):
        """
        Handles update tables request.
        """

        def handler_filter(data_model, update):
            """
            Admin wants to update all tables.
            """

            user_context = get_user_context(data_model, update)
            message_text = update.message.text.strip().lower()
            return (user_context.administrative_permission and
                    user_context.action == UserAction.ADMIN_TABLE_MANAGEMENT
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
            await TableManagementController.send_with_table_management_panel(
                context.bot,
                chat_id
            )
            return True

        return (handler_filter, handler)

    def handle_other_messages(self):
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
            await TableManagementController.send_with_table_management_panel(
                context.bot,
                chat_id
            )
            return True

        return (handler_filter, handler)

    def query_handler_add_page(self):
        """
        Handles inline query add/remove page.
        """

        def handler_filter(data_model, update):
            user_id = update.callback_query.from_user.id
            user_context = data_model.users.get_user_context(user_id)
            action = TableManagementController.InlineKeyboardData.decode(
                update.callback_query.data
            ).action
            return (user_context.administrative_permission and
                    action is
                    TableManagementController.QUERY_ACTION_SWITCH_PAGE)

        async def handler(data_model, update, _context):
            query = update.callback_query
            table_id = query.message.text.splitlines()[2][4:]
            page = TableManagementController.InlineKeyboardData.decode(
                query.data
            ).data
            data_model.workout_table_names.switch_pages(table_id, page)
            reply_keyboard = self.inline_keyboard_table_pages(
                data_model,
                table_id
            )
            await query.edit_message_text(text=query.message.text,
                                          reply_markup=reply_keyboard)
            await query.answer()

        return (handler_filter, handler)

    def query_handler_change_table(self):
        """
        Handles inline query change table.
        """

        def handler_filter(data_model, update):
            user_id = update.callback_query.from_user.id
            user_context = data_model.users.get_user_context(user_id)
            action = TableManagementController.InlineKeyboardData.decode(
                update.callback_query.data
            ).action
            return (user_context.administrative_permission and
                    action is
                    TableManagementController.QUERY_ACTION_CHOOSE_TABLE)

        async def handler(data_model, update, context):
            query = update.callback_query
            user_id = update.callback_query.from_user.id
            user_context = data_model.users.get_user_context(user_id)
            chat_id = user_context.chat_id
            table_id = TableManagementController.InlineKeyboardData.decode(
                update.callback_query.data
            ).data
            table_name = data_model.workout_plans.get_plan_name(table_id)

            text = "Редактирование таблицы\n"
            text += get_table_name_message(table_name, table_id)
            text += "id: " + escape_text(table_id) + "\n"
            text += "\n"
            text += "Отметьте страницы с тренировками"

            reply_markup = self.inline_keyboard_table_pages(
                data_model,
                table_id
            )
            await context.bot.send_message(chat_id, text,
                                           reply_markup=reply_markup,
                                           parse_mode="MarkdownV2")
            await query.answer()

        return (handler_filter, handler)
