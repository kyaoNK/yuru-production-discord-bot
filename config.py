from dotenv import load_dotenv
from logging import getLogger
import os

logger = getLogger("discord")

def load_config():
    try:
        config_file_dir = os.path.dirname(__file__)
        
        load_dotenv(dotenv_path=config_file_dir + '/.env')

        # Notion設定
        notion_api_key = os.environ.get('NOTION_API_KEY')
        user_database_id = os.environ.get('USER_DATABASE_ID')
        progress_database_id = os.environ.get('PROGRESS_DATABASE_ID')

        if not all([notion_api_key, user_database_id, progress_database_id]):
            raise ValueError("Missing required Notion environment variables")

        user_database_url = f"https://api.notion.com/v1/databases/{user_database_id}/query"
        progress_database_url = f"https://api.notion.com/v1/databases/{progress_database_id}/query"

        headers = {
            "Notion-Version": "2022-06-28",
            "Authorization": f"Bearer {notion_api_key}",
            "Content-Type": "application/json"
        }

        # Discord設定
        discord_token = os.environ.get('DISCORD_TOKEN')
        reminder_channel_id = os.environ.get('REMINDER_CHANNEL_ID')

        if not all([discord_token, reminder_channel_id]):
            raise ValueError("Missing required Discord environment variables")

        try:
            reminder_channel_id = int(reminder_channel_id)
        except ValueError:
            raise ValueError("REMINDER_CHANNEL_ID must be an integer")
        
        # 絶対パス設定
        yuru_discord_bot_dirpath = os.environ.get('YURU_DISCORD_BOT_DIRPATH')
        
        return {
            "NOTION_API_KEY": notion_api_key,
            "USER_DATABASE_ID": user_database_id,
            "PROGRESS_DATABASE_ID": progress_database_id,
            "USER_DATABASE_URL": user_database_url,
            "PROGRESS_DATABASE_URL": progress_database_url,
            "HEADERS": headers,
            "DISCORD_TOKEN": discord_token,
            "REMINDER_CHANNEL_ID": reminder_channel_id,
            "YURU_DISCORD_BOT_DIRPATH": yuru_discord_bot_dirpath
        }
        
    except Exception as e:
        logger.error(f"Error loading configuration: {e}", exc_info=True)
        raise

try:
    config = load_config()
    
    # グローバル変数として設定
    globals().update(config)
    
    logger.info("Configuration loaded successfully")
except Exception as e:
    logger.critical(f"Failed to load configuration: {e}")
    raise