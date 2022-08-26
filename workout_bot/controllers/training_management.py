"""
Provides user interaction for training.
"""

from telegram import Update
from telegram import ReplyKeyboardMarkup, KeyboardButton
from data_model.users import UserAction
from view.workouts import get_workout_text_message
from view.workouts import get_week_routine_text_message


class TrainingManagement:
    """
    Provides user interaction for training.
    """

    def __init__(self, bot, data_model):
        self.bot = bot
        self.data_model = data_model

    async def send_with_next_or_all_buttons(self, chat_id, user_context,
                                            message):
        """
        Sends message and adds buttons "Далее", "Все действия"
        """

        keyboard = [[KeyboardButton("Все действия"), KeyboardButton("Далее")]]
        if user_context.administrative_permission:
            key_admin = [KeyboardButton("Администрирование")]
            keyboard.append(key_admin)
        reply_markup = ReplyKeyboardMarkup(keyboard)
        await self.bot.send_message(chat_id,
                                    message,
                                    disable_web_page_preview=True,
                                    reply_markup=reply_markup,
                                    parse_mode="MarkdownV2")

    async def change_plan_prompt(self, chat_id, user_context):
        """
        Asks the user with user_id to choose plan.
        """

        table_id = user_context.current_table_id
        if (not table_id
                or not self.data_model.workout_plans
                .is_table_id_present(table_id)):
            await self.bot \
                .send_message(chat_id, "Вам не назначена программа тренировок")
            return

        plans = self.data_model.workout_plans.get_plan_names(table_id)
        if plans:
            keyboard = []
            text = 'Выберите программу из списка:'
            for plan in plans:
                text += '\n - ' + plan
                keyboard.append([KeyboardButton(plan)])
            reply_markup = ReplyKeyboardMarkup(keyboard)
            await self.bot.send_message(chat_id, text,
                                        reply_markup=reply_markup)
        else:
            await self.bot \
                .send_message(chat_id, "Для вас ещё нет программы тренировок.")

    async def change_plan(self, chat_id, user_context, plan):
        """
        Changes plan to the selected one for user.
        """

        plans = (
            self.data_model
            .workout_plans.get_plan_names(user_context.current_table_id)
        )
        if plan in plans:
            user_context.current_page = plan
            user_context.current_week = \
                self.data_model.workout_plans \
                    .get_week_number(user_context.current_table_id,
                                     user_context.current_page) - 1
            user_context.current_workout = 0
            self.data_model.users.set_user_context(user_context)
            self.data_model.users.set_user_action(user_context.user_id,
                                                  UserAction.TRAINING)
            await self.bot.send_message(chat_id, 'Программа выбрана.')
            await self.send_week_schedule(chat_id, user_context)
            await self.send_workout(chat_id, user_context)
        else:
            await self.bot.send_message(chat_id, 'Нет такой программы.')
            await self.change_plan_prompt(chat_id, user_context)

    async def send_week_schedule(self, chat_id, user_context):
        """
        Sends week workout schedule.
        """

        message = get_week_routine_text_message(self.data_model,
                                                user_context.current_table_id,
                                                user_context.current_page,
                                                user_context.current_week)
        await self.send_with_next_or_all_buttons(chat_id, user_context,
                                                 message)

    async def send_workout(self, chat_id, user_context):
        """
        Sends workout.
        """

        message = get_workout_text_message(self.data_model,
                                           user_context.current_table_id,
                                           user_context.current_page,
                                           user_context.current_week,
                                           user_context.current_workout)
        await self.send_with_next_or_all_buttons(chat_id, user_context,
                                                 message)

    async def send_all_actions(self, chat_id):
        """
        Sends extended keyboard with all the keys.
        """

        keyboard = [
            [KeyboardButton("Сменить программу")],
            [
                KeyboardButton("Начальная неделя"),
                KeyboardButton("Последняя неделя")
            ],
            [
                KeyboardButton("Прошлая неделя"),
                KeyboardButton("Следующая неделя")
            ],
            [KeyboardButton("Следующая тренировка")],
            [KeyboardButton("Перейти к тренировкам")],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard)
        await self.bot.send_message(chat_id,
                                    "Доступные действия:",
                                    reply_markup=reply_markup,
                                    parse_mode="MarkdownV2")

    async def handle_message(self, update: Update):
        """
        Handles user messages.
        Returns True if messsage was processed, False otherwise.
        """

        user_id = update.message.from_user.id
        chat_id = update.effective_chat.id
        user_context = self.data_model.users.get_user_context(user_id)
        message_text = update.message.text.strip().lower()

        if user_context.action == UserAction.CHOOSING_PLAN:
            await self.change_plan(chat_id,
                                   user_context,
                                   update.message.text.strip())
            return True

        if user_context.action == UserAction.TRAINING:
            if (user_context.current_table_id is None
                    or user_context.current_page is None):
                await self.data_model \
                    .users.set_user_action(user_id, UserAction.CHOOSING_PLAN)
            if (message_text in ("выбрать программу", "сменить программу",
                                 "поменять программу")):
                self.data_model.users.set_user_action(user_id,
                                                      UserAction.CHOOSING_PLAN)
                await self.change_plan_prompt(chat_id, user_context)

            if message_text in ("далее", "следующая тренировка"):
                week_previous = user_context.current_week
                self.data_model.next_workout_for_user(user_id)
                if week_previous != user_context.current_week:
                    # show week schedule if week changes
                    self.send_week_schedule(chat_id, user_context)
                await self.send_workout(chat_id, user_context)
                return True

            if message_text == "все действия":
                await self.send_all_actions(chat_id)
                return True

            if message_text in ("первая неделя", "начальная неделя"):
                user_context.current_week = 0
                user_context.current_workout = 0
                self.data_model.users.set_user_context(user_context)
                await self.send_week_schedule(chat_id, user_context)
                await self.send_workout(chat_id, user_context)
                return True

            if (message_text in ("последняя неделя",
                                 "крайняя неделя", "текущая неделя")):
                user_context.current_week = self.data_model.workout_plans \
                    .get_week_number(user_context.current_table_id,
                                     user_context.current_page) - 1
                user_context.current_workout = 0
                self.data_model.users.set_user_context(user_context)
                await self.send_week_schedule(chat_id, user_context)
                await self.send_workout(chat_id, user_context)
                return True

            if message_text == "следующая неделя":
                if user_context.current_week < self.data_model.workout_plans \
                        .get_week_number(user_context.current_table_id,
                                         user_context.current_page) - 1:
                    user_context.current_week += 1
                user_context.current_workout = 0
                self.data_model.users.set_user_context(user_context)
                await self.send_week_schedule(chat_id, user_context)
                await self.send_workout(chat_id, user_context)
                return True

            if message_text in ("прошлая неделя", "предыдущая неделя"):
                if user_context.current_week > 0:
                    user_context.current_week -= 1
                user_context.current_workout = 0
                self.data_model.users.set_user_context(user_context)
                await self.send_week_schedule(chat_id, user_context)
                await self.send_workout(chat_id, user_context)
                return True

        return False
