from datetime import datetime
from typing import Any

from psycopg2.extras import RealDictRow

from src.database.database import Database
from src.database.database_keys import DATABASEKEYS
from src.error_handler.error_handler import ErrorHandler


class UserDataDataBaseService(Database):
    _instance = None
    _init = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init:
            return
        self.ErrorHandler = ErrorHandler().logger("Userdata database service")
        super().__init__()
        self._init = True

    def get_user_data_by_id(self, user_id: int) -> dict:
        userdata = self.find_item_in_sql(
            table=DATABASEKEYS.TABLES.USERDATA,
            item=DATABASEKEYS.USERDATA.USER_ID,
            value=user_id,
        )
        return dict(userdata)
        pass

    def get_user_data_by_username(self, user_name: str) -> dict | None:
        userdata = self.find_item_in_sql(
            table=DATABASEKEYS.TABLES.USERDATA,
            item=DATABASEKEYS.USERDATA.USER_NAME,
            value=user_name,
        )
        return dict(userdata) if userdata else None

    def get_user_data_by_email(self, email: str) -> dict | None:
        userdata = self.find_item_in_sql(
            table=DATABASEKEYS.TABLES.USERDATA,
            item=DATABASEKEYS.USERDATA.EMAIL,
            value=email,
        )
        return dict(userdata) if userdata else None

    def get_user_data_by_email_or_username(self, value: Any) -> dict | None:
        con, cur = self.connect_db()
        try:
            cur.execute(
                f"""SELECT * FROM {DATABASEKEYS.TABLES.USERDATA}
                WHERE {DATABASEKEYS.USERDATA.USER_NAME} = %s
                OR {DATABASEKEYS.USERDATA.EMAIL} = %s""",
                (
                    value,
                    value,
                ),
            )
            con.commit()

            userdata = cur.fetchone()
            return dict(userdata) if userdata else None
        except Exception as e:
            self.Erro
            return None
        finally:
            if con:
                self.close_db(conn=con)

    def insert_new_userdata(
        self, email: str, display_name: str, username: str, password: str
    ) -> bool:
        con, cur = self.connect_db()
        try:
            current_time = datetime.now()
            cur.execute(
                f"""INSERT INTO {DATABASEKEYS.TABLES.USERDATA} ({DATABASEKEYS.USERDATA.EMAIL},
                {DATABASEKEYS.USERDATA.DISPLAY_NAME},
                {DATABASEKEYS.USERDATA.USER_NAME},
                {DATABASEKEYS.USERDATA.PASSWORD},
                {DATABASEKEYS.USERDATA.CREATED_TIME},
                {DATABASEKEYS.USERDATA.MODIFIED_TIME})
                VALUES(%s,%s,%s,%s,%s,%s)""",
                (email, display_name, username, password, current_time, current_time),
            )
            con.commit()
            con.close()
            if cur.rowcount >= 1:
                return True
            return False
        except Exception as e:
            self.ErrorHandler.error("failed to insert new userdata", {e})
            return False
        finally:
            if con:
                self.close_db(conn=con)
        pass

    def insert_new_user_with_provider_data(
        self,
        email: str,
        display_name: str,
        username: str,
        password: str,
        provider: str,
        provider_id: str,
    ) -> bool:
        con, cur = self.connect_db()
        current_time = datetime.now()
        try:
            cur.execute(
                f"""INSERT INTO {DATABASEKEYS.TABLES.USERDATA}
                ({DATABASEKEYS.USERDATA.EMAIL},
                {DATABASEKEYS.USERDATA.DISPLAY_NAME},
                {DATABASEKEYS.USERDATA.USER_NAME},
                {DATABASEKEYS.USERDATA.PASSWORD},
                {DATABASEKEYS.USERDATA.CREATED_TIME},
                {DATABASEKEYS.USERDATA.MODIFIED_TIME},
                {DATABASEKEYS.USERDATA.PROVIDER},
                {DATABASEKEYS.USERDATA.PROVIDER_ID})
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""",
                (
                    email,
                    display_name,
                    username,
                    password,
                    current_time,
                    current_time,
                    provider,
                    provider_id,
                ),
            )
            con.commit()
            con.close()
            if cur.rowcount >= 1:
                return True
            return False
        except Exception as e:
            self.ErrorHandler.error("failed to insert new userdata with provider", {e})
            return False
        finally:
            if con:
                self.close_db(conn=con)

    def update_user_password(self, user_id: str, new_hashed_password: str) -> bool:
        return self.update_db(
            table=DATABASEKEYS.TABLES.USERDATA,
            item=DATABASEKEYS.USERDATA.USER_ID,
            value=user_id,
            item_to_update=DATABASEKEYS.USERDATA.PASSWORD,
            value_to_update=new_hashed_password,
        )

    def update_user_avatar_and_modified_time(
        self, user_id: str, avatar_path: str, modified_time: str
    ) -> bool:
        con, cur = self.databaseService.connect_db()
        # update path, and modified time
        try:
            cur.execute(
                f"""
                UPDATE {DATABASEKEYS.TABLES.USERDATA}
                SET {DATABASEKEYS.USERDATA.AVARTAR} = %s,
                {DATABASEKEYS.USERDATA.MODIFIED_TIME} =%s
                WHERE {DATABASEKEYS.USERDATA.USER_ID} = %s;""",
                (avatar_path, modified_time, user_id),
            )
            con.commit()
            return True
        except Exception as e:
            self.ErrorHandler.logger("User_data").error(
                "Failed to update user avatar to postges", {e}
            )
            return False
        finally:
            self.close_db(conn=con)

    def update_trips_modified_time(self, user_id: str, modified_time: str) -> bool:
        try:
            update = self.update_db(
                table=DATABASEKEYS.TABLES.USERDATA,
                item=DATABASEKEYS.USERDATA.USER_ID,
                value=user_id,
                item_to_update=DATABASEKEYS.USERDATA.TRIPS_MODIFIED_TIME,
                value_to_update=modified_time,
            )
            return update
        except Exception as e:
            print(e)
            return False
