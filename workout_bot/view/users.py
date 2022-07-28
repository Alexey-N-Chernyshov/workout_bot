def get_user_message(data_model, user_id):
    text = ""
    user_context = data_model.users.get_user_context(user_id)
    if user_context:
        if user_context.username:
            text += "@" +  user_context.username
        if (user_context.first_name or user_context.last_name):
            text += " -"
        if user_context.first_name:
            text += " " +  user_context.first_name
        if user_context.last_name:
            text += " " +  user_context.last_name
    else:
        text += "пользователь не найден"
    if text:
        text += ", "
    text += "id: " + str(user_id)
    return text
