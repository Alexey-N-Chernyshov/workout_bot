def user_to_text_message(user_context):
    text = ""
    is_username_printed = False
    if user_context.username:
        text += "@" + user_context.username
        is_username_printed = True
    if text and (user_context.first_name or user_context.last_name):
        text += " -"
    if user_context.first_name:
        if text:
            text += " "
        text += user_context.first_name
    if user_context.last_name:
        if text:
            text += " "
        text += user_context.last_name
    if not is_username_printed:
        if text:
            text += ", "
        text += "id: " + str(user_context.user_id)
    return text


def get_user_message(data_model, user_id):
    text = ""
    user_context = data_model.users.get_user_context(user_id)
    if user_context:
        text = user_to_text_message(user_context)
    else:
        text = "пользователь не найден, id: " + str(user_id)
    return text
