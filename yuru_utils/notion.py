from config import NOTION_API_KEY, EDITOR_DB_ID, PROGRESS_DB_ID, DEFAULT_N_DAY
import datetime
import pytz
from notion_client import Client, APIErrorCode, APIResponseError
from yuru_utils.logger import get_logger

logger = get_logger("discord")

yuru_notion_client = Client(auth=NOTION_API_KEY)

progress_list = [ "1.撮影済み", "2.編集中", "3.チーフチェック中", "4.修正中", "5.premiere提出済み", "6.パーソナリティチェック中", "7.修正・入稿中", "8.入稿済み", "9.アーカイブ済み" ]

def get_editor_data() -> dict:
    results = query_notion_DB(EDITOR_DB_ID)
    editor_dict = dict()

    for res in results:
        properties = res.get("properties", {})
        editor_name = properties.get("編集者", {}).get("people",[{}])[0].get("name","")
        notion_user_id_str = properties.get("編集者", {}).get("people",[{}])[0].get("id","")
        discord_user_id_str = properties.get("DiscordID", {}).get("rich_text",[])[0].get("text",{}).get("content", "")
        if editor_name and discord_user_id_str.isdigit():
            editor_dict[editor_name] = { "notion_user_id": notion_user_id_str, "discord_user_id": int(discord_user_id_str) }
        else:
            logger.warning(f"Invalid editor data: name={editor_name}, id={discord_user_id_str}")
        
    logger.info(f"Notion's editor name and DiscordID were obtained for Notion's editor database.")
    return editor_dict

def get_progress_data(days: int = DEFAULT_N_DAY, editor_id: str="") -> (dict, dict):

    now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))

    release_date_properties       = [ create_property("公開日", "date", "equals", (now + datetime.timedelta(days=d)).strftime("%Y-%m-%d")) for d in range(days) ]
    editorial_deadline_properties = [ create_property("編集締め切り", "date", "equals", (now + datetime.timedelta(days=d)).strftime("%Y-%m-%d")) for d in range(days) ]
    
    release_date_progress_properties       = [ create_property("進捗", "select", "equals", progress) for progress in progress_list[0:7] ]
    editorial_deadline_progress_properties = [ create_property("進捗", "select", "equals", progress) for progress in progress_list[0:4] ]

    release_date_filter       = logic_property( "and", [ logic_property("or", release_date_progress_properties)       , logic_property("or", release_date_properties )     ] + ([ create_property("入稿担当", "people", "contains", editor_id) ] if editor_id else [] ))
    editorial_deadline_filter = logic_property( "and", [ logic_property("or", editorial_deadline_progress_properties) , logic_property("or", editorial_deadline_properties)] + ([ create_property("編集者"  , "people", "contains", editor_id) ] if editor_id else [] ))
    
    release_date_results   = query_notion_DB(PROGRESS_DB_ID, release_date_filter)
    editorial_deadline_results = query_notion_DB(PROGRESS_DB_ID, editorial_deadline_filter)
    
    release_date_dict = dict()
    for res in release_date_results:
        properties = res.get("properties", [])
        title = "".join(t.get("text",{}).get("content", "") for t in properties.get("タイトル",{}).get("title",[{}])).replace("_", " ")
        submitters_name = [person.get("name", "") for person in properties.get("入稿担当", {}).get("people", [{}])]
        release_date = properties.get("公開日", {}).get("date",{}).get("start", "")
        youtube_channel = properties.get("番組", {}).get("select", {}).get("name", "")
    
        release_date_dict[title] = {
            "release_date": release_date,
            "submitters_name": submitters_name,
            "youtube_channel": youtube_channel,
        }
        
    editorial_deadline_dict = dict()
    for res in editorial_deadline_results:
        properties = res.get("properties", {})
        title = "".join(t.get("text",{}).get("content", "") for t in properties.get("タイトル",{}).get("title",[{}])).replace("_", " ")
        editors_name = [editor.get("name", "") for editor in properties.get("編集者", {}).get("people", [{}])]
        editorial_deadline_date = properties.get("編集締め切り",{}).get("date",{}).get("start", "")
        youtube_channel = properties.get("番組", {}).get("select", {}).get("name", "")
        
        editorial_deadline_dict[title] = {
            "editorial_deadline_date": editorial_deadline_date,
            "editors_name": editors_name,
            "youtube_channel": youtube_channel,
        }
    
    logger.info(f"{(now).strftime('%Y-%m-%d')}~{(now + datetime.timedelta(days=days)).strftime('%Y-%m-%d')}\nrelease_date:{release_date_dict}\neditorial_deadline:{editorial_deadline_dict}")
                
    return release_date_dict, editorial_deadline_dict

def create_property(property: str, type: str, field: str, value: str) -> dict:
    return {
        "property": property,
        type: {
            field: value,
        }
    }
    
def logic_property(logic: str, properties: list):
    if logic == "and" or logic == "or":
        return { logic: properties }
    else:
        logger.warning(f"logic_key is not 'or' or 'and'. logic_arg={logic}")
        return {}

def query_notion_DB(database_id:str, filter: list = list()) -> dict:
    try:
        query_params = dict()
        query_params["database_id"] = database_id
        query_params["page_size"] = 100
        
        if filter:
            query_params["filter"] = filter
        
        loop_cnt = 0
        has_more = True
        data = list()
        while has_more:
            loop_cnt += 1
            if not loop_cnt == 1:
                query_params["start_cursor"] = next_cursor
            response = yuru_notion_client.databases.query(**query_params)
            data += response.get("results", [])
            has_more = response.get("has_more")
            next_cursor = response.get("next_cursor")
        
        return data
    
    except APIResponseError as e:
        if e.code == APIErrorCode.ObjectNotFound:
            logger.error("The requested object was not found. The page was not found. Please check the page ID.", exc_info=True)
        elif e.code == APIErrorCode.Unauthorized:
            logger.error("Unauthorized access. You are not authorized to access this page.", exc_info=True)
        elif e.code == APIErrorCode.RateLimited:
            logger.error("Rate Limit reached. You have hit the rate limit. Please try again later.")
        elif e.code == APIErrorCode.ValidationError:
            logger.warning("Validation error occurred. Please check the validity of the data being sent to the Notion API. Details: %s", e.message, exc_info=True)
            return {}
        else:
            logger.error(f"An error occurred: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"An unexpeted error occurred: {e}", exc_info=True)

    return {}