import discord
from discord import app_commands
from discord.ext import tasks
import os
import requests
import datetime

import config
import utils

# Botの設定
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    """
        サーバ起動時のログ出力
    """
    print(f"We have logged in as {client.user}")
    print(f"discord.py version{discord.__version__}")
    print(f"REMINDER_CHANNEL_ID type: {type(config.REMINDER_CHANNEL_ID)}")
    
    reminder.start()
    
    await tree.sync()
    
@tree.command(description="ユーザの直近のタスクを表示する")
async def my_task(interaction: discord.Interaction):
    """
    コマンド /my_task を入力されたらそのユーザの直近のタスクをメッセージで送信
    """
    await interaction.response.defer(ephemeral=True)

    user_mention = interaction.user.mention
    user_id = interaction.user.id

    user_data = utils.get_user_data()
    user_name = [k for k, v in user_data.items() if v == user_id][0]

    publication_date_dict, editorial_deadline_dict = utils.get_progress_data()

    message_statement = user_mention + "\n"

    if not (any(publication_date_dict) or any(editorial_deadline_dict)):
        message_statement = "直近の3日間のタスクはない"

    else:
        if any(publication_date_dict):
            message_statement += "**公開予定**\n"

        for key, value in publication_date_dict.items():
            for name in value["publication_people_name"]:
                if name == user_name:
                    message_statement += f"{value['publication_date']} | {key}\n"

        if any(publication_date_dict):
            message_statement += "\n**編集締め切り**\n"

        for key, value in editorial_deadline_dict.items():
            for name in value["editor_people_name"]:    
                if name == user_name:
                    message_statement += f"{value['editorial_deadline_date']} | {key}\n"

    await interaction.followup.send(message_statement)    

@tasks.loop(seconds=60)
async def reminder():
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=config.DIFF_JST_FROM_UTC)
    print(f"h:m={now.hour}:{now.minute}")
    
    if now.hour == 1 and now.minute == 0 :
        print("リマンイダー開始")
        channel = client.get_channel(config.REMINDER_CHANNEL_ID)
        
        if channel is not None:    
            user_data = utils.get_user_data()
            publication_date_dict, editorial_deadline_dict = utils.get_progress_data()

            message_statement = utils.make_message_statement(user_data, publication_date_dict, editorial_deadline_dict)
            
            await channel.send(message_statement)
            print("リマンイダー成功")
        else:
            print("Channel not found!")

@reminder.before_loop
async def before_reminder():
    await client.wait_until_ready()

client.run(config.DISCORD_TOKEN)