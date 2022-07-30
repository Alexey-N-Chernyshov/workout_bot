from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from data_model.users import UserAction


class Administration:
    def __init__(self, bot, data_model):
        self.bot = bot
        self.data_model = data_model

    def show_admin_panel(self, chat_id, user_context):
        if user_context.administrative_permission:
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                           one_time_keyboard=True)
            key_table_management = KeyboardButton(text='Управление таблицами')
            keyboard.add(key_table_management)
            key_remove_workout_link = \
                KeyboardButton(text="Удалить ссылку на упражнение")
            key_add_workout_link = \
                KeyboardButton(text="Добавить ссылку на упражнение")
            keyboard.row(key_remove_workout_link, key_add_workout_link)
            key_training = KeyboardButton(text='Перейти к тренировкам')
            keyboard.add(key_training)
            self.bot.send_message(chat_id, "Администрирование",
                                reply_markup=keyboard,
                                parse_mode="MarkdownV2")

    def remove_excercise_link_prompt(self, chat_id, user_context):
        name = user_context.user_input_data.name
        link = self.data_model.excercise_links[name]
        text = "Удалить упражнение?\n\n[{}]({})".format(name, link)
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        key_no = KeyboardButton(text="Нет")
        key_yes = KeyboardButton(text="Да")
        keyboard.row(key_no, key_yes)
        self.bot.send_message(chat_id, text, disable_web_page_preview=True,
                              reply_markup=keyboard, parse_mode="MarkdownV2")

    def add_excercise_link_prompt(chat_id, user_context):
        name = user_context.user_input_data.name
        link = user_context.user_input_data.link
        text = "Добавить упражнение?\n\n[{}]({})".format(name, link)
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        key_no = KeyboardButton(text="Нет")
        key_yes = KeyboardButton(text="Да")
        keyboard.row(key_no, key_yes)
        self.bot.send_message(chat_id, text, disable_web_page_preview=True,
                              reply_markup=keyboard, parse_mode="MarkdownV2")

    def handle_message(self, message):
        user_context = \
            self.data_model.users.get_user_context(message.from_user.id)
        message_text = message.text.strip().lower()

        if user_context is None or not user_context.administrative_permission:
            return False

        if user_context.action == UserAction.admin_removing_excercise_name:
            name = message_text
            if name in self.data_model.excercise_links:
                user_context.user_input_data.name = name
                self.remove_excercise_link_prompt(message.chat.id, user_context)
                user_context.action = UserAction.admin_removing_excercise_prove
            else:
                self.bot.send_message(message.chat.id, "Нет такого упражнения")
                user_context.action = UserAction.administration
                self.show_admin_panel(message.chat.id, user_context)
            return True

        if user_context.action == UserAction.admin_removing_excercise_prove:
            if message_text == "да":
                del self.data_model \
                    .excercise_links[user_context.user_input_data.name]
                user_context.action = UserAction.administration
                user_context.user_input_data = None
                self.show_admin_panel(message.chat.id, user_context)
            elif message_text == "нет":
                user_context.action = UserAction.administration
                user_context.user_input_data = None
                self.show_admin_panel(message.chat.id, user_context)
            else:
                self.remove_excercise_link_prompt(message.chat.id, user_context)
            return True

        if user_context.action == UserAction.admin_adding_excercise_name:
            user_context.user_input_data.name = message_text
            self.bot.send_message(message.chat.id, "Введите ссылку")
            user_context.action = UserAction.admin_adding_excercise_link
            return True

        if user_context.action == UserAction.admin_adding_excercise_link:
            user_context.user_input_data.link = message.text.strip()
            self.add_excercise_link_prompt(message.chat.id, user_context)
            user_context.action = UserAction.admin_adding_excercise_prove
            return True

        if user_context.action == UserAction.admin_adding_excercise_prove:
            if message_text == "да":
                self.data_model\
                    .excercise_links[user_context.user_input_data.name] = \
                    user_context.user_input_data.link
                user_context.action = UserAction.administration
                user_context.user_input_data = None
                self.show_admin_panel(message.chat.id, user_context)
            elif message_text == "нет":
                user_context.action = UserAction.administration
                user_context.user_input_data = None
                self.show_admin_panel(message.chat.id, user_context)
            else:
                self.add_excercise_link_prompt(message.chat.id, user_context)
            return True

        # change user action commands
        if user_context.action == UserAction.administration:
            if message_text == "перейти к тренировкам":
                # return to above menu
                return False

            if message_text == "удалить ссылку на упражнение":
                user_context.action = UserAction.admin_removing_excercise_name
                user_context.user_input_data = RemoveExcerciseLinkContext()
                self.bot.send_message(message.chat.id,
                                      "Введите название упражнения")
                return True

            if message_text == "добавить ссылку на упражнение":
                user_context.action = UserAction.admin_adding_excercise_name
                user_context.user_input_data = AddExcerciseLinkContext()
                self.bot.send_message(message.chat.id,
                                      "Введите название упражнения")
                return True

            self.show_admin_panel(message.chat.id, user_context)
            return True


        return False
