"""
Helper functions.
"""

def get_user_context(data_model, update):
    """
    Helper function, returns user_context of message sender.
    """

    user_id = update.message.from_user.id
    return data_model.users.get_user_context(user_id)
