"""
Telegram bot related code resides here.
"""

from telegram import Update
from telegram.ext import (
    filters, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler
)
from controllers.controllers import Controllers
from controllers.training_management import start_training
from data_model.users import UserAction
from view.utils import escape_text


class TelegramBot:
    """
    Telegram bot class.
    """

    def __init__(self, application, loader, data_model, version):
        self.telegram_application = application
        self.bot = application.bot
        self.data_model = data_model
        self.version = version

        # init controllers
        self.controllers = Controllers(loader, data_model)

        self.telegram_application.add_handler(
            CommandHandler("start", self.handle_start)
        )

        self.telegram_application.add_handler(
            CommandHandler("system_stats", self.handle_system_stats)
        )

        self.telegram_application.add_handler(
            CommandHandler("about", self.handle_command_about)
        )

        self.telegram_application.add_handler(
            MessageHandler(filters.TEXT, self.handle_message)
        )

        self.telegram_application.add_handler(
            CallbackQueryHandler(self.handle_query)
        )

    async def register_commands(self):
        """
        Registers the list of commands.
        """

        await self.bot.set_my_commands(
            [
                ("start", "Starts bot, use for restart in case of trouble."),
                ("system_stats", "Some runtime statistics."),
                ("about", "About a bot.")
            ]
        )

    def start_bot(self):
        """
        Starts telegram bot and enters infinity polling loop.
        """

        self.telegram_application.run_polling()

    async def handle_start(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Handler for command /start that initializes a new user.
        """

        self.data_model.statistics.record_command()
        if update.effective_chat.type != "private":
            await self.bot.send_message(
                update.effective_chat.id,
                "Бот доступен только в приватном чате"
            )
            return
        user_context = self.data_model \
            .users.get_or_create_user_context(update.message.from_user.id)
        user_context.user_id = update.message.from_user.id
        user_context.first_name = update.message.from_user.first_name
        user_context.last_name = update.message.from_user.last_name
        user_context.username = update.message.from_user.username
        user_context.chat_id = update.effective_chat.id
        user_context.current_page = None
        user_context.current_week = None
        user_context.current_workout = None

        if not (self.data_model.users
                .is_user_awaiting_authorization(user_context.user_id)
                or self.data_model.users
                .is_user_blocked(user_context.user_id)):
            user_context.action = UserAction.CHOOSING_PLAN
            self.data_model.users.set_user_context(user_context)
            await start_training(self.data_model, update, context)
            return

        self.data_model.users.set_user_context(user_context)
        await self.handle_message(update, context)

    async def handle_system_stats(
            self,
            update: Update,
            _context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Handler for command /system_stats shows statistics.
        """

        self.data_model.statistics.record_command()
        user_context = self.data_model \
            .users.get_user_context(update.message.from_user.id)

        text = "Системная статистика:\n\n"
        time = self.data_model.statistics.get_training_plan_update_time()
        text += f"Расписание обновлено: {time:%Y-%m-%d %H:%M}\n"

        if user_context and user_context.administrative_permission:
            text += "Количество запросов: "
            text += str(self.data_model.statistics.get_total_requests()) + "\n"
            text += "Количество команд: "
            text += str(self.data_model.statistics.get_total_commands()) + "\n"
            text += "Количество пользователей: "
            text += str(self.data_model.users.get_users_number()) + "\n"

        await self.bot.send_message(update.effective_chat.id, text)

    async def handle_command_about(
            self,
            update: Update,
            _context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Handler for command '/about'
        """

        self.data_model.statistics.record_command()
        text = "*Бот для тренировок*\n"
        text += f"Версия: {escape_text(self.version)}\n"
        link = escape_text(
            "https://github.com/Alexey-N-Chernyshov/workout_bot"
        )
        text += f"[Github]({link})"
        await self.bot.send_message(
            update.effective_chat.id,
            text,
            disable_web_page_preview=True,
            parse_mode="MarkdownV2"
        )

    async def handle_message(self, update: Update,
                             context: ContextTypes.DEFAULT_TYPE):
        """
        Handles all text messages.
        """

        self.data_model.statistics.record_request()
        await self.controllers.handle_message(
            self.data_model,
            update,
            context
        )

    async def handle_query(self, update: Update,
                           context: ContextTypes.DEFAULT_TYPE):
        """
        Handlers for inline queries.
        """

        query = update.callback_query
        await self.controllers.handle_query(self.data_model, update, context)
        await query.answer()
