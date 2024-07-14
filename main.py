import discord
from discord import app_commands
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

@client.event
async def on_ready():
    """
        サーバ起動時のログ出力
    """
    print(f"We have logged in as {client.user}")
    print(f"discord.py version{discord.__version__}")
    await tree.sync()

client.run(config.DISCORD_TOKEN)
