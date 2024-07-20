from yuru_utils.logger import get_logger

logger = get_logger("discord")

def make_message_statement(editor_data: dict, release_date_dict: dict,editorial_deadline_dict: dict) -> str:
    """
    進捗状況をDiscordに表示するためのメッセージ文を作成する
    """
    try:
        message_statement = "**公開予定**"
        for key, value in release_date_dict.items():                
            u_id = [ v["discord_user_id"] for k, v in editor_data.items() if k in value["submitters_name"] ]
            str_u_id = "".join(f"<@{u}> " for u in u_id)
            message_statement += f"\n{value['youtube_channel']} | {value['release_date']} | {str_u_id}| {key}"

        message_statement += "\n**編集締切**"
        for key, value in editorial_deadline_dict.items():
            
            u_id = [ v["discord_user_id"] for k, v in editor_data.items() if k in value["editors_name"] ]
            str_u_id = "".join(f"<@{u}> " for u in u_id)
            message_statement += f"\n{value['youtube_channel']} | {value['editorial_deadline_date']} | {str_u_id}| {key}"
            
        return message_statement

    except Exception as e:
        logger.error(f"Error creating message statement: {e}", exc_info=True)
        return "メッセージの作成中にエラーが発生しました。管理者に連絡してください。"
    