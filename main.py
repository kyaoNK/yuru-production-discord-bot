import discord
from discord import app_commands
import os
import requests
import datetime

# Notion設定
NOTION_API_KEY = os.environ['NOTION_API_KEY']
USER_DATABASE_ID = os.environ['USER_DATABASE_ID']
PROGRESS_DATABASE_ID = os.environ['PROGRESS_DATABASE_ID']

USER_DATABASE_URL = f"https://api.notion.com/v1/databases/{USER_DATABASE_ID}/query"
PROGRESS_DATABASE_URL = f"https://api.notion.com/v1/databases/{PROGRESS_DATABASE_ID}/query"

HEADERS = {
    "Notion-Version": "2022-06-28",
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json"
}

# Botの設定
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)


def get_user_data() -> dict:
    """
    NotionのユーザーデータベースからNotionのユーザー名とDiscordIDを取得
    """
    user_database = requests.post(USER_DATABASE_URL, headers=HEADERS).json()

    user_data = {}
    for result in user_database.get("results", []):
        properties = result.get("properties", {})
        user_name = properties.get("編集者", {}).get("people",[{}])[0].get("name","")
        user_id = int(properties.get("DiscordID", {}).get("rich_text",[])[0].get("text",{}).get("content", ""))
        user_data[user_name] = user_id
    return user_data


def get_progress_data() -> (dict, dict):
    """
    Notionの進捗管理データベースから今日から3日間で公開予定と編集締め切りの情報を取得
    """
    today = datetime.date.today()
    day_range = 3  # 3日間

    editorial_deadline_dict = dict()
    publication_date_dict = dict()

    for i in range(day_range):
        print((today + datetime.timedelta(days=i)).strftime("%Y-%m-%d"))

        # 公開日
        json_data = {
            "filter": {
                "property": "公開日",
                "date": {
                    "equals":
                    (today + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
                }
            }
        }

        data = requests.post(PROGRESS_DATABASE_URL, headers=HEADERS, json=json_data).json()

        for result in data.get("results", []):
            properties = result.get("properties", {})
            
            title = properties.get("タイトル",{}).get("title",[{}])[0].get("text",{}).get("content", "")
            publication_people = properties.get("入稿担当", {}).get("people", [{}])
            publication_people_name = list()
            for publication_person in publication_people:
                publication_people_name.append(publication_person.get("name", ""))    
            publication_date = properties.get("公開日", {}).get("date",{}).get("start", "")
            
            publication_date_dict[title] = {
                "publication_date": publication_date,
                "publication_people_name": publication_people_name
            }

        # 編集締め切り
        json_data = {
            "filter": {
                "property": "編集締め切り",
                "date": {
                    "equals":
                    (today + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
                }
            }
        }

        data = requests.post(PROGRESS_DATABASE_URL,
                            headers=HEADERS,
                            json=json_data).json()

        for result in data.get("results", []):
            properties = result.get("properties", {})
            title = properties.get("タイトル",{}).get("title",[{}])[0].get("text",{}).get("content", "")

            editor_people = properties.get("編集者", {}).get("people", [{}])
            editor_people_name = list()
            for editor in editor_people:
                editor_people_name.append(editor.get("name", ""))
            editorial_deadline_date = properties.get("編集締め切り",{}).get("date",{}).get("start", "")
            
            editorial_deadline_dict[title] = {
                "editorial_deadline_date": editorial_deadline_date,
                "editor_people_name": editor_people_name
            }
            
    return publication_date_dict, editorial_deadline_dict


def make_message_statement(user_data: dict, publication_date_dict: dict,editorial_deadline_dict: dict) -> str:
    """
    進捗状況をDiscordに表示するためのメッセージ文を作成する
    """

    print(f"user_data: {user_data}")

    message_statement = "**公開予定**\n"
    for key, value in publication_date_dict.items():
        u_id = [ v for k, v in user_data.items() if k in value["publication_people_name"] ]
        str_u_id = ""
        for u in u_id:
            str_u_id += f"<@{u}> "
        print(f"入稿担当{str_u_id}")
        message_statement += f"{value['publication_date']} | {str_u_id}| {key}\n"

    message_statement += "\n**編集締め切り**\n"
    for key, value in editorial_deadline_dict.items():
        u_id = [ v for k, v in user_data.items() if k in value["editor_people_name"] ]
        str_u_id = ""
        for u in u_id:
            str_u_id += f"<@{u}> "
        print(f"編集者{str_u_id}")
        message_statement += f"{value['editorial_deadline_date']} | {str_u_id}| {key}\n"

    return message_statement


@tree.command(description="ユーザの直近のタスクを表示する")
async def my_task(interaction: discord.Interaction):
    """
    コマンド /my_task を入力されたらそのユーザの直近のタスクをメッセージで送信
    """
    await interaction.response.defer(ephemeral=True)

    user_mention = interaction.user.mention
    user_id = interaction.user.id

    user_data = get_user_data()
    user_name = [k for k, v in user_data.items() if v == user_id][0]

    print(f"user_mention:{user_mention}")
    print(f"user_id:{user_id}")
    print(f"user_name:{user_name}")

    publication_date_dict, editorial_deadline_dict = get_progress_data()

    message_statement = user_mention + "\n"

    if not (any(publication_date_dict) or any(editorial_deadline_dict)):
        message_statement = "直近の3日間のタスクはない"

    else:
        if any(publication_date_dict):
            message_statement += "**公開予定**\n"

        for key, value in publication_date_dict.items():
            if value["publication_user_name"] == user_name:
                message_statement += f"{value['publication_date']} | {key}\n"

        if any(publication_date_dict):
            message_statement += "\n**編集締め切り**\n"

        for key, value in editorial_deadline_dict.items():
            if value["editor"] == user_name:
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

@client.event
async def on_message(message: discord.Message):
    """
    メッセージ受信時
    """
    ch_name = "test"

    if message.author.bot:
        return

    user_data = get_user_data()
    publication_date_dict, editorial_deadline_dict = get_progress_data()

    message_statement = make_message_statement(user_data, publication_date_dict, editorial_deadline_dict)

    if message.channel.name == ch_name:
        try:
            await message.channel.send(message_statement)
        except Exception as excep:
            print(f"VARIABLES ABOVE!\n{excep}")


    DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
    client.run(DISCORD_TOKEN)
