from dotenv import load_dotenv
import os

def load_config():
    config_file_dir = os.path.dirname(__file__)
    
    load_dotenv(dotenv_path=config_file_dir + "/.env")

    # Notion設定
    notion_api_key = os.environ.get("NOTION_API_KEY")
    editor_DB_id = os.environ.get("EDITOR_DB_ID")
    progress_DB_id = os.environ.get("PROGRESS_DB_ID")

    if not all([notion_api_key, editor_DB_id, progress_DB_id]):
        raise ValueError("Missing required Notion environment variables.")

    # Discord設定
    discord_token = os.environ.get("DISCORD_TOKEN")
    reminder_channel_id = os.environ.get("REMINDER_CHANNEL_ID")

    if not all([discord_token, reminder_channel_id]):
        raise ValueError("Missing required Discord environment variables.")

    try:
        reminder_channel_id = int(reminder_channel_id)
    except ValueError:
        raise ValueError("REMINDER_CHANNEL_ID must be an integer.")
    
    # 絶対パス設定
    yuru_discord_bot_dirpath = os.environ.get("YURU_DISCORD_BOT_DIRPATH")
    
    # デフォルトの日数分
    default_n_days = os.environ.get("DEFAULT_N_DAY")
    try:
        default_n_days = int(default_n_days)
    except ValueError:
        raise ValueError("DEFAULT_N_DAYS must be an integer.")
    
    return {
        "NOTION_API_KEY": notion_api_key,
        "EDITOR_DB_ID": editor_DB_id,
        "PROGRESS_DB_ID": progress_DB_id,
        "DISCORD_TOKEN": discord_token,
        "REMINDER_CHANNEL_ID": reminder_channel_id,
        "YURU_DISCORD_BOT_DIRPATH": yuru_discord_bot_dirpath,
        "DEFAULT_N_DAY": default_n_days,
    }
    
config = load_config()

# グローバル変数として設定
globals().update(config)