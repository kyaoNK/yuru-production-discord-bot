import discord
import asyncio

import config
import utils
import main

async def send_message():
    await main.client.wait_until_ready()
    channel = main.client.get_channel(config.REMINDER_CHANNEL_ID)
    
    if channel is not None:    
        user_data = utils.get_user_data()
        publication_date_dict, editorial_deadline_dict = utils.get_progress_data()

        message_statement = utils.make_message_statement(user_data, publication_date_dict, editorial_deadline_dict)
        
        await channel.send(message_statement)

async def reminder():
    """
    リマインダー
    """
    print("リマインダー開始")
    async with main.client:
        await send_message()
        await main.client.start(config.DISCORD_TOKEN)
        
    print("リマインダー完了")
    
asyncio.run(reminder())