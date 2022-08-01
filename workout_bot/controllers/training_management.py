"""
Provides user interaction for training.
"""

from telebot.types import ReplyKeyboardMarkup, KeyboardButton
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

    def send_with_next_or_all_buttons(self, chat_id, user_context, message):
        """
        Sends message and adds buttons "Далее", "Все действия"
        """

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        key_all = KeyboardButton(text='Все действия')
        key_next = KeyboardButton(text='Далее')
        keyboard.row(key_all, key_next)

        if user_context.administrative_permission:
            key_admin = KeyboardButton(text='Администрирование')
            keyboard.add(key_admin)

        self.bot.send_message(chat_id, message, disable_web_page_preview=True,
                              reply_markup=keyboard, parse_mode="MarkdownV2")

    def change_plan_prompt(self, chat_id, user_context):
        """
        Asks the user with user_id to choose plan.
        """

        table_id = user_context.current_table_id
        if (not table_id
                or not self.data_model.workout_plans
                .is_table_id_present(table_id)):
            self.bot.send_message(chat_id,
                                  "Вам не назначена программа тренировок")
            return

        plans = self.data_model.workout_plans.get_plan_names(table_id)
        if plans:
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            text = 'Выберите программу из списка:'
            for plan in plans:
                text += '\n - ' + plan
                button = KeyboardButton(text=plan)
                keyboard.add(button)
            self.bot.send_message(chat_id, text, reply_markup=keyboard)
        else:
            self.bot.send_message(chat_id,
                                  "Для вас ещё нет программы тренировок.")

    def change_plan(self, chat_id, user_context, plan):
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
            self.bot.send_message(chat_id, 'Программа выбрана.')
            self.send_week_schedule(chat_id, user_context)
            self.send_workout(chat_id, user_context)
        else:
            self.bot.send_message(chat_id, 'Нет такой программы.')
            self.change_plan_prompt(chat_id, user_context)

    def send_week_schedule(self, chat_id, user_context):
        """
        Sends week workout schedule.
        """

        message = get_week_routine_text_message(self.data_model,
                                                user_context.current_table_id,
                                                user_context.current_page,
                                                user_context.current_week)
        self.send_with_next_or_all_buttons(chat_id, user_context, message)

    def send_workout(self, chat_id, user_context):
        """
        Sends workout.
        """

        message = get_workout_text_message(self.data_model,
                                           user_context.current_table_id,
                                           user_context.current_page,
                                           user_context.current_week,
                                           user_context.current_workout)
        self.send_with_next_or_all_buttons(chat_id, user_context, message)

    def send_all_actions(self, chat_id):
        """
        Sends extended keyboard with all the keys.
        """

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        key_change_plan = KeyboardButton(text='Сменить программу')
        keyboard.add(key_change_plan)
        key_first_week = KeyboardButton(text='Начальная неделя')
        key_last_week = KeyboardButton(text='Последняя неделя')
        keyboard.row(key_first_week, key_last_week)
        key_previous_week = KeyboardButton(text='Прошлая неделя')
        key_next_week = KeyboardButton(text='Следующая неделя')
        keyboard.row(key_previous_week, key_next_week)
        key_next = KeyboardButton(text='Следующая тренировка')
        keyboard.add(key_next)
        key_training = KeyboardButton(text='Перейти к тренировкам')
        keyboard.add(key_training)
        self.bot.send_message(chat_id, "Доступные действия:",
                              reply_markup=keyboard,
                              parse_mode="MarkdownV2")

    def handle_message(self, message):
        """
        Handles user messages.
        Returns True if messsage was processed, False otherwise.
        """

        user_context = \
            self.data_model.users.get_user_context(message.from_user.id)
        message_text = message.text.strip().lower()

        if user_context.action == UserAction.CHOOSING_PLAN:
            self.change_plan(message.chat.id,
                             user_context, message.text.strip())
            return True

        if user_context.action == UserAction.TRAINING:
            if (user_context.current_table_id is None
                    or user_context.current_page is None):
                self.data_model.users.set_user_action(user_context.user_id,
                                                      UserAction.CHOOSING_PLAN)
            if (message_text in ("выбрать программу", "сменить программу",
                                 "поменять программу")):
                self.data_model.users.set_user_action(user_context.user_id,
                                                      UserAction.CHOOSING_PLAN)
                self.change_plan_prompt(message.chat.id, user_context)

            if message_text in ("далее", "следующая тренировка"):
                if user_context.current_workout < self.data_model\
                        .workout_plans \
                        .get_workout_number(user_context.current_table_id,
                                            user_context.current_page,
                                            user_context.current_week) - 1:
                    user_context.current_workout += 1
                    self.data_model.users.set_user_context(user_context)
                elif user_context.current_week < self.data_model \
                        .workout_plans \
                        .get_week_number(user_context.current_table_id,
                                         user_context.current_page) - 1:
                    user_context.current_week += 1
                    user_context.current_workout = 0
                    self.data_model.users.set_user_context(user_context)
                    self.send_week_schedule(message.chat.id, user_context)
                self.send_workout(message.chat.id, user_context)
                return True

            if message_text == "все действия":
                self.send_all_actions(message.chat.id)
                return True

            if message_text in ("первая неделя", "начальная неделя"):
                user_context.current_week = 0
                user_context.current_workout = 0
                self.data_model.users.set_user_context(user_context)
                self.send_week_schedule(message.chat.id, user_context)
                self.send_workout(message.chat.id, user_context)
                return True

            if (message_text in ("последняя неделя",
                                 "крайняя неделя", "текущая неделя")):
                user_context.current_week = self.data_model.workout_plans \
                    .get_week_number(user_context.current_table_id,
                                     user_context.current_page) - 1
                user_context.current_workout = 0
                self.data_model.users.set_user_context(user_context)
                self.send_week_schedule(message.chat.id, user_context)
                self.send_workout(message.chat.id, user_context)
                return True

            if message_text == "следующая неделя":
                if user_context.current_week < self.data_model.workout_plans \
                        .get_week_number(user_context.current_table_id,
                                         user_context.current_page) - 1:
                    user_context.current_week += 1
                user_context.current_workout = 0
                self.data_model.users.set_user_context(user_context)
                self.send_week_schedule(message.chat.id, user_context)
                self.send_workout(message.chat.id, user_context)
                return True

            if message_text in ("прошлая неделя", "предыдущая неделя"):
                if user_context.current_week > 0:
                    user_context.current_week -= 1
                user_context.current_workout = 0
                self.data_model.users.set_user_context(user_context)
                self.send_week_schedule(message.chat.id, user_context)
                self.send_workout(message.chat.id, user_context)
                return True

        return False
