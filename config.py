import os

# Notion設定
NOTION_API_KEY = os.environ['NOTION_API_KEY']
USER_DATABASE_ID = os.environ['USER_DATABASE_ID']
PROGRESS_DATABASE_ID = os.environ['PROGRESS_DATABASE_ID']
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']

USER_DATABASE_URL = f"https://api.notion.com/v1/databases/{USER_DATABASE_ID}/query"
PROGRESS_DATABASE_URL = f"https://api.notion.com/v1/databases/{PROGRESS_DATABASE_ID}/query"

HEADERS = {
    "Notion-Version": "2022-06-28",
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json"
}

REMINDER_CHANNEL_ID = os.environ['REMINDER_CHANNLE_ID']
