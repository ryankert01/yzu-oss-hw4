# MyGo DB file credits: @StevenShih-0402

import json
from typing import Optional

class MyGoImage:
    def __init__(self, image_db_filepath: str):
        # Load and index once
        with open(image_db_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self._name_to_link = {item['圖片名稱']: item['圖片連結'] for item in data}
        self._names        = list(self._name_to_link.keys())

    def searchMyGoImage(self, keyword: str) -> Optional[str]:
        """
        Return the URL of the first image whose name contains `keyword`.
        If nothing matches, returns None.
        """
        for name in self._names:
            if keyword in name:
                return self._name_to_link[name]
        return None
