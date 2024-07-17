import requests
import os
import datetime
import pytz
from logging import getLogger

import config

logger = getLogger("discord")

def get_user_data() -> dict:
    """
    NotionのユーザーデータベースからNotionのユーザー名とDiscordIDを取得
    """
    try:
        response = requests.post(config.USER_DATABASE_URL, headers=config.HEADERS)
        response.raise_for_status()
        user_database = response.json()

        user_data = {}
        for result in user_database.get("results", []):
            properties = result.get("properties", {})
            user_name = properties.get("編集者", {}).get("people",[{}])[0].get("name","")
            user_id_str = properties.get("DiscordID", {}).get("rich_text",[])[0].get("text",{}).get("content", "")
            if user_name and user_id_str.isdigit():
                user_data[user_name] = int(user_id_str)
            else:
                logger.warning(f"Invalid user data: name={user_name}, id={user_id_str}")
            
        logger.info(f"Notion's user name and DiscordID were obtained for Notion's editor database.")
        return user_data
    
    except requests.RequestException as e:
        logger.error(f"Error fetching user data: {e}", exc_info=True)
        return {}
    

def get_progress_data_for_3days() -> (dict, dict):
    """
    Notionの進捗管理データベースから今日から3日間で公開予定と編集締め切りの情報を取得
    """
    try:
        now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        days = 3  # 3日間

        editorial_deadline_dict = dict()
        publication_date_dict = dict()

        for i in range(days):
            # 公開日
            json_data = { "filter": { "property": "公開日", "date": { "equals": (now + datetime.timedelta(days=i)).strftime("%Y-%m-%d") }}}
            
            response = requests.post(config.PROGRESS_DATABASE_URL, headers=config.HEADERS, json=json_data)
            response.raise_for_status()
            data = response.json()

            for result in data.get("results", []):
                properties = result.get("properties", {})
                
                title = properties.get("タイトル",{}).get("title",[{}])[0].get("text",{}).get("content", "").replace("_", " ")
                publication_people = properties.get("入稿担当", {}).get("people", [{}])
                publication_people_name = [person.get("name", "") for person in publication_people] 
                publication_date = properties.get("公開日", {}).get("date",{}).get("start", "")
                
                publication_date_dict[title] = {
                    "publication_date": publication_date,
                    "publication_people_name": publication_people_name
                }

            # 編集締め切り
            json_data = { "filter": { "property": "編集締め切り", "date": { "equals": (now + datetime.timedelta(days=i)).strftime("%Y-%m-%d") }}}

            response = requests.post(config.PROGRESS_DATABASE_URL, headers=config.HEADERS, json=json_data)
            response.raise_for_status()
            data = response.json()

            for result in data.get("results", []):
                properties = result.get("properties", {})
                title = properties.get("タイトル",{}).get("title",[{}])[0].get("text",{}).get("content", "").replace("_", " ")
                editor_people = properties.get("編集者", {}).get("people", [{}])
                editor_people_name = [editor.get("name", "") for editor in editor_people]
                editorial_deadline_date = properties.get("編集締め切り",{}).get("date",{}).get("start", "")
                
                editorial_deadline_dict[title] = {
                    "editorial_deadline_date": editorial_deadline_date,
                    "editor_people_name": editor_people_name
                }
                
        logger.info(f"{(now).strftime('%Y-%m-%d')}~{(now + datetime.timedelta(days=days)).strftime('%Y-%m-%d')} | publication_date:{publication_date_dict}, editorial_deadline:{editorial_deadline_dict}")
                
        return publication_date_dict, editorial_deadline_dict
    except requests.RequestException as e:
        logger.error(f"Error fetching user data: {e}", exc_info=True)
        return {}, {}

def make_message_statement(user_data: dict, publication_date_dict: dict,editorial_deadline_dict: dict) -> str:
    """
    進捗状況をDiscordに表示するためのメッセージ文を作成する
    """
    try:
        message_statement = "**公開予定**\n"
        for key, value in publication_date_dict.items():
            u_id = [ v for k, v in user_data.items() if k in value["publication_people_name"] ]
            str_u_id = "".join(f"<@{u}> " for u in u_id)
            message_statement += f"{value['publication_date']} | {str_u_id}| {key}\n"

        message_statement += "\n**編集締め切り**\n"
        for key, value in editorial_deadline_dict.items():
            u_id = [ v for k, v in user_data.items() if k in value["editor_people_name"] ]
            str_u_id = "".join(f"<@{u}> " for u in u_id)
            message_statement += f"{value['editorial_deadline_date']} | {str_u_id}| {key}\n"
            
        return message_statement
    except Exception as e:
        logger.error(f"Error creating message statement: {e}", exc_info=True)
        return "メッセージの作成中にエラーが発生しました。管理者に連絡してください。"