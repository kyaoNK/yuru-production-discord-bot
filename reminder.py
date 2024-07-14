import discord

import config
import utils
import main

def reminder():
    """
    リマインダー
    """

    user_data = utils.get_user_data()
    publication_date_dict, editorial_deadline_dict = utils.get_progress_data()

    message_statement = utils.make_message_statement(user_data, publication_date_dict, editorial_deadline_dict)

    try:
        channel = main.client.get_channel(config.REMINDER_CHANNEL_ID)
        channel.send(message_statement)
    except Exception as excep:
        print(f"VARIABLES ABOVE!\n{excep}")