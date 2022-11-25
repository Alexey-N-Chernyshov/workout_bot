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
from google_sheets_feeder.google_sheets_loader import GoogleSheetsLoader
from google_sheets_feeder.utils import get_table_id_from_link
from telegram_bot.utils import get_user_context


async def send_with_table_management_panel(bot, chat_id,
                                           text="Управление таблицами"):
    """
    Shows table management panel.
    """

    keyboard = [
        [KeyboardButton("Показать все таблицы")],
        [KeyboardButton("Добавить таблицу")],
        [KeyboardButton("Прочитать таблицы")],
        [KeyboardButton("Администрирование")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await bot.send_message(chat_id, text, reply_markup=reply_markup,
                           parse_mode="MarkdownV2")


def inline_keyboard_table_pages(data_model, table_id):
    """
    Builds InlineKeyboard with all pages in table.
    """

    pages = GoogleSheetsLoader().get_sheet_names(table_id)
    pages_present = data_model.workout_table_names.get_plan_names(table_id)
    keyboard = []
    for page in pages:
        if page in pages_present:
            page_text = "✅ " + page
        else:
            page_text = "⏺ " + page
        keyboard.append([InlineKeyboardButton(page_text, callback_data=page)])
    return InlineKeyboardMarkup(keyboard, resize_keyboard=True)


def handle_go_table_management():
    """
    Handles switch to training status.
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
        await context.bot.send_message(chat_id, "Введите ссылку на таблицу",
                                       reply_markup=reply_markup)

    return (handler_filter, handler)


def handle_cancel_add_table():
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
        await send_with_table_management_panel(context.bot, chat_id)

    return (handler_filter, handler)


def handle_add_table_pages():
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
            reply_markup = inline_keyboard_table_pages(data_model, table_id)
            await context.bot.send_message(chat_id, text,
                                           reply_markup=reply_markup,
                                           parse_mode="MarkdownV2")
            data_model.users.set_user_action(user_context.user_id,
                                             UserAction.ADMIN_TABLE_MANAGEMENT)
            await send_with_table_management_panel(context.bot,
                                                   update.effective_chat.id)
        except (AttributeError, TypeError):
            text = "Ошибка при загрузке таблицы"
            await context.bot.send_message(chat_id, text)
            keyboard = [[KeyboardButton("Отмена")], ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await context.bot.send_message(chat_id,
                                           "Введите ссылку на таблицу",
                                           reply_markup=reply_markup)

        return True

    return (handler_filter, handler)


def handle_update_tables():
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
        await send_with_table_management_panel(context.bot, chat_id)
        return True

    return (handler_filter, handler)


# TODO handle delete/update pages for existing table


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
    handle_cancel_add_table(),
    handle_add_table_pages(),
    handle_update_tables(),
    handle_other_messages()
]


def query_handler_add_page():
    """
    Handles inline query add/remove page.
    """

    def handler_filter(data_model, update):
        user_id = update.callback_query.from_user.id
        user_context = data_model.users.get_user_context(user_id)
        return user_context.administrative_permission

    async def handler(data_model, update, _context):
        query = update.callback_query

        table_id = query.message.text.splitlines()[2][4:]
        page = query.data
        data_model.workout_table_names.switch_pages(table_id, page)
        reply_keyboard = inline_keyboard_table_pages(data_model, table_id)
        await query.edit_message_text(text=query.message.text,
                                      reply_markup=reply_keyboard)
        await query.answer()

    return (handler_filter, handler)


table_management_query_handlers = [
    query_handler_add_page()
]
