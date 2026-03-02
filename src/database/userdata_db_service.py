from src.database.database import Database
from datetime import datetime
from src.database.database_keys import DATABASEKEYS
class UserDataDataBaseService (Database):
    _instance = None
    _init = False
    def __new__(cls):
        if cls._instance is None :
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._init:
            return  
        super().__init__()
        self._init = True

    
    def update_userdata_version(self, user_id: int) -> tuple[bool, int | None]:
        try:
            con, cur = self.connect_db()

            cur.execute(f"""
                UPDATE {DATABASEKEYS.TABLES.USERDATA}
                SET {DATABASEKEYS.USERDATA.USER_DATA_VERSION} =
                    {DATABASEKEYS.USERDATA.USER_DATA_VERSION} + 1
                WHERE {DATABASEKEYS.USERDATA.USER_ID} = %s
                RETURNING {DATABASEKEYS.USERDATA.USER_DATA_VERSION}
            """, (user_id,))

            row = cur.fetchone()
            con.commit()

            if row:
                return True, row[0]  # return new version
            return False, None

        except Exception as e:
            print(e)
            return False, None

    