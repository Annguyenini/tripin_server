from datetime import datetime
from typing import Any

from psycopg2.extras import RealDictRow

from src.database.database import Database
from src.database.database_keys import DATABASEKEYS
from src.error_handler.error_handler import ErrorHandler


class UserSettingsDataBaseService(Database):
    _instance = None
    _init = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init:
            return
        self.ErrorHandler = ErrorHandler().logger("User settings database service")
        super().__init__()
        self._init = True

    def get_user_settings_from_database(self, user_id: int):
        settings = self.find_item_in_sql(
            table=DATABASEKEYS.TABLES.USER_SETTINGS,
            item=DATABASEKEYS.USER_SETTINGS.USER_ID,
            value=user_id,
        )
        return settings

    def update_user_settings(self, clauses: str, values: list) -> bool:
        con, cur = self.connect_db()
        table = DATABASEKEYS.TABLES.USER_SETTINGS
        try:
            cur.execute(
                f"""
                UPDATE {table} SET {clauses} WHERE {DATABASEKEYS.USER_SETTINGS.USER_ID} = %s
                """,
                (values),
            )
            con.commit()
            if cur.rowcount <= 0:
                return False

            return True
        except Exception as e:
            self.ErrorHandler.logger("fail to update user setting", str(e))
            return False

        finally:
            self.close_db(conn=con)
