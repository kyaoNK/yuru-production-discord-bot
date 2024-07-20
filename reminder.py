from discord.ext import tasks
import datetime
import pytz
from config import REMINDER_CHANNEL_ID, DEFAULT_N_DAY
from yuru_utils.utils import make_message_statement
from yuru_utils.notion import get_editor_data, get_progress_data
from yuru_utils.logger import get_logger
from discord_client import yuru_discord_client

logger = get_logger("discord")

reminder_hour = 12
reminder_minute = 52

@tasks.loop(seconds=60)
async def reminder():
    try:
        now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        
        if now.hour == reminder_hour and now.minute == reminder_minute :
            
            logger.info(f"The designated time has arrived.")
            channel = yuru_discord_client.get_channel(REMINDER_CHANNEL_ID)
            
            if channel is not None:    
                editor_data = get_editor_data()
                release_date_dict, editorial_deadline_dict = get_progress_data(DEFAULT_N_DAY)

                message_statement = make_message_statement(editor_data, release_date_dict, editorial_deadline_dict)
                
                await channel.send(message_statement)
                logger.info(f"Sent you reminder notices for your tasks.\nMessage: \n{message_statement}")
            else:
                logger.info(f"Channel not found!")
    except Exception as e:
        logger.error(f"Error in reminder task: {e}", exc_info=True)
        await channel.send("タスクの取得中にエラーが発生しました。管理者に連絡してください。")

@reminder.before_loop
async def before_reminder():
    await yuru_discord_client.wait_until_ready()