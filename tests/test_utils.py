import unittest
from config import DEFAULT_N_DAY
from yuru_utils.notion import get_editor_data, get_progress_data
from yuru_utils.utils import make_message_statement

import pprint

class TestYuruUtils(unittest.TestCase):
    def test_get_editor_data(self):
        editor_data = get_editor_data()
        
        print("======== editor_data ========")
        pprint.pprint(editor_data)
        
        self.assertIsInstance(editor_data, dict)
        self.assertTrue(all(isinstance(key, str) and isinstance(value["discord_user_id"], int) and isinstance(value["notion_user_id"], str) for key, value in editor_data.items()))
        
    def test_get_progress_data(self):
        days = DEFAULT_N_DAY
        
        print("======== editor_id is kyao ========")
        editor_notion_id = "a25aaebe-4778-4638-882b-1ee5652d24ec"
        release_data_dict, editorial_deadline_dict = get_progress_data(days, editor_id=editor_notion_id)
        pprint.pprint(release_data_dict)
        pprint.pprint(editorial_deadline_dict)
        
        self.assertIsInstance(release_data_dict, dict)
        self.assertIsInstance(editorial_deadline_dict, dict)
        
        print("======== editor_id is None ========")
        release_data_dict, editorial_deadline_dict = get_progress_data(days)
        pprint.pprint(release_data_dict)
        pprint.pprint(editorial_deadline_dict)
        
        self.assertIsInstance(release_data_dict, dict)
        self.assertIsInstance(editorial_deadline_dict, dict)
        
    def test_make_message_statement(self):
        editor_data = {
            "test_editor": {
                "discord_user_id": 759419430420742154,
                "notion_user_id": "a25aaebe-4778-4638-882b-1ee5652d24ec"
            }
        }
        release_date_dict = {
            "Test Task": {
                "release_date": "2024-01-01",
                "submitters_name": ["test_editor"],
                "youtube_channel": "test_ch"
            }
        }
        editorial_deadline_dict = {
            "Test Task 2": {
                "editorial_deadline_date": "2024-01-02",
                "editors_name": ["test_editor"],
                "youtube_channel": "test_ch"
            }
        }
        messaage_statement = make_message_statement(editor_data, release_date_dict, editorial_deadline_dict)
        
        print(f"message_statement\n{messaage_statement}")
        
if __name__=="__main__":
    unittest.main()