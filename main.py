from discord import app_commands, errors

from yuru_utils.logger import setup_logger
from config import YURU_DISCORD_BOT_DIRPATH, DISCORD_TOKEN
from reminder import reminder
from commands import setup_commands
from discord_client import yuru_discord_client

log_file = YURU_DISCORD_BOT_DIRPATH + "/logs/yuru_notice_discord.log"

logger = setup_logger("discord", log_file)

# Botの設定
tree = app_commands.CommandTree(yuru_discord_client)
setup_commands(tree)

@yuru_discord_client.event
async def on_ready():
    try:
        reminder.start()
        await tree.sync()
        logger.info(f"We have logged in as {yuru_discord_client.user.name}[{yuru_discord_client.user.id}].")
    except Exception as e:
        logger.error(f"Error in on_ready: {e}", exc_info=True)

if __name__=="__main__":
    try:
        yuru_discord_client.run(DISCORD_TOKEN, log_handler=None)
    except errors.LoginFailure:
        logger.error("Failed to login. Please check your token.")
    except Exception as e:
        logger.error(f"An error occurred while running the bot: {e}", exc_info=True)