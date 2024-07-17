from discord import Intents, AutoShardedClient, Interaction, app_commands, errors
from discord.ext import tasks
import os
import datetime
import pytz
from logging import getLogger, handlers, StreamHandler, Formatter, INFO

import config
import yuru_utils

# Loggerの設定
logger = getLogger("discord")
logger.setLevel(INFO)
rot_file_handler = handlers.RotatingFileHandler(
    filename="/home/src/yuru_notification/logs/yuru_notice_discord.log",
    encoding="utf-8",
    maxBytes=32*1024*1024,
    backupCount=5,
)
dt_fmt = "%Y-%m-%d %H:%M:%S"
formatter = Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style='{')
rot_file_handler.setFormatter(formatter)
logger.addHandler(rot_file_handler)

stream_handler = StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

logger.info("Successfully configured the logger.")

# Botの設定
intents = Intents.default()
intents.message_content = True
intents.members = True
client = AutoShardedClient(intents=intents, shard_count=2)

tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    try:
        reminder.start()
        await tree.sync()
        logger.info(f"We have logged in as {client.user.name}[{client.user.id}].")
    except Exception as e:
        logger.error(f"Error in on_ready: {e}", exc_info=True)

@tree.command(description="ユーザの直近3日間のタスクを表示する")
async def my_task(interaction: Interaction):
    """
    コマンド my_task を入力されたらそのユーザの直近のタスクをメッセージで送信
    """
    try:
        await interaction.response.defer(ephemeral=True)
        
        logger.info(f"Command my_task is called.")

        user_mention = interaction.user.mention
        user_id = interaction.user.id

        user_data = yuru_utils.get_user_data()
        user_name = [k for k, v in user_data.items() if v == user_id][0]

        publication_date_dict, editorial_deadline_dict = yuru_utils.get_progress_data_for_3days()
        
        # フィルター処理
        filtered_publication_date_dict = {title: info for title, info in publication_date_dict.items() if user_name in info["publication_people_name"] }
        logger.info(f"filtered publication_date_dict: {filtered_publication_date_dict}")
        
        filtered_editorial_deadline_dict = {title: info for title, info in editorial_deadline_dict.items() if user_name in info["editor_people_name"] }
        logger.info(f"filtered editorial_deadline_dict: {filtered_editorial_deadline_dict}")
        
        message_statement = user_mention

        if not (filtered_publication_date_dict or filtered_editorial_deadline_dict):
            message_statement += "\n直近の3日間のタスクはない"
            logger.info(f"publication_date_dict and editorial_deadline_dict are empty.")

        else:
            if filtered_publication_date_dict:
                message_statement += "\n**公開予定**\n"

            for key, value in filtered_publication_date_dict.items():
                for name in value["publication_people_name"]:
                    if name == user_name:
                        message_statement += f"{value['publication_date']} | {key}\n"

            if filtered_editorial_deadline_dict:
                message_statement += "\n**編集締め切り**\n"

            for key, value in filtered_editorial_deadline_dict.items():
                for name in value["editor_people_name"]:
                    if name == user_name:
                        message_statement += f"{value['editorial_deadline_date']} | {key}\n"

        await interaction.followup.send(message_statement)
        logger.info(f"Send a message about the user\'s tasks.")
    except errors.NotFound as e:
        logger.error(f"Interaction not found: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Error in my_task command: {e}", exc_info=True)
        await interaction.followup.send("タスクの取得中にエラーが発生しました。管理者に連絡してください。", ephemeral=True)

@tasks.loop(seconds=60)
async def reminder():
    try:
        now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        
        if now.hour == 11 and now.minute == 20 :
            
            logger.info(f"The designated time has arrived.")
            channel = client.get_channel(config.REMINDER_CHANNEL_ID)
            
            if channel is not None:    
                user_data = yuru_utils.get_user_data()
                publication_date_dict, editorial_deadline_dict = yuru_utils.get_progress_data_for_3days()

                message_statement = yuru_utils.make_message_statement(user_data, publication_date_dict, editorial_deadline_dict)
                
                await channel.send(message_statement)
                logger.info(f"Sent you reminder notices for your tasks.\nMessage: \n{message_statement}")
            else:
                logger.info(f"Channel not found!")
    except Exception as e:
        logger.error(f"Error in reminder task: {e}", exc_info=True)
        await channel.send("タスクの取得中にエラーが発生しました。管理者に連絡してください。")

@reminder.before_loop
async def before_reminder():
    await client.wait_until_ready()

if __name__=="__main__":
    try:
        client.run(config.DISCORD_TOKEN, log_handler=None)
    except errors.LoginFailure:
        logger.error("Failed to login. Please check your token.")
    except Exception as e:
        logger.error(f"An error occurred while running the bot: {e}", exc_info=True)