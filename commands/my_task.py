from discord import Interaction, errors, app_commands
from config import DEFAULT_N_DAY
from yuru_utils.notion import get_editor_data , get_progress_data
from yuru_utils.logger import get_logger

logger = get_logger("discord")


@app_commands.describe(n_days="今日から何日分のタスクがほしいか入力してください。")
async def my_task(interaction: Interaction, n_days: str = str(DEFAULT_N_DAY)):
    try:
        n_days = n_days.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
        
        if not ( n_days.isdigit() and 1 <= int(n_days)<= 7 ):
            logger.error(f"A number other than 2 through 7 was entered in n_days. n_dyas={n_days}", exc_info=True)
            await interaction.response.send_message("オプションの日数には1～7の数字のみを入れてください。", ephemeral=True)
        
        n_days = int(n_days)
        
        await interaction.response.defer(ephemeral=True)
        logger.info(f"Command my_task is called.")

        user_mention = interaction.user.mention
        user_id = interaction.user.id
        
        editor_notion_id = [ v["notion_user_id"] for _, v in get_editor_data().items() if v["discord_user_id"] == user_id][0]
        release_date_dict, editorial_deadline_dict = get_progress_data(n_days, editor_id=editor_notion_id)
        
        message_statement = user_mention

        if not (release_date_dict or editorial_deadline_dict):
            message_statement += f"\n{( '今日' if n_days == 1 else '明日まで' if n_days == 2 else '直近の'+str(n_days)+'日間' )}のタスクはない"
            logger.info(f"release_date_dict and editorial_deadline_dict are empty.")

        else:
            if release_date_dict:
                message_statement += "\n**公開予定**\n"

            for key, value in release_date_dict.items():
                message_statement += f"{value['release_date']} | {key}\n"

            if editorial_deadline_dict:
                message_statement += "\n**編集締め切り**\n"

            for key, value in editorial_deadline_dict.items():
                message_statement += f"{value['editorial_deadline_date']} | {key}\n"

        await interaction.followup.send(message_statement)
        logger.info(f"Send a message about the user\'s tasks.")
    except errors.NotFound as e:
        logger.error(f"Interaction not found: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Error in my_task command: {e}", exc_info=True)
        await interaction.followup.send("タスクの取得中にエラーが発生しました。管理者に連絡してください。", ephemeral=True)