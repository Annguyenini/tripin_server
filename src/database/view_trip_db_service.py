import logging
from datetime import datetime

from src.database.database import Database
from src.database.database_keys import DATABASEKEYS
from src.error_handler.error_handler import ErrorHandler


class ViewTripDatabaseService(Database):
    _instance = None
    _init = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init:
            return
        self.ErrorHandler = ErrorHandler().logger("share view trip")
        super().__init__()
        self._init = True

    def get_trip_data_from_trip_view_token(self, token: str) -> dict | None:
        data = self.find_item_in_sql(
            table=DATABASEKEYS.TABLES.TRIP_SHARED_LINKS,
            item=DATABASEKEYS.TRIP_SHARED_LINKS.TOKEN,
            value=token,
        )
        return data

    def get_all_trip_data_from_trip_view_token(self, token: str) -> dict | None:
        # return trip contents, trip name and user name
        con, cur = self.connect_db()
        try:
            cur.execute(
                f"""
                SELECT sl.*,
                tb.{DATABASEKEYS.TRIPS.TRIP_NAME},
                tb.{DATABASEKEYS.TRIPS.IMAGE_KEY},
                ud.{DATABASEKEYS.USERDATA.DISPLAY_NAME}
                FROM {DATABASEKEYS.TABLES.TRIP_SHARED_LINKS} as sl
                INNER JOIN {DATABASEKEYS.TABLES.TRIPS} as tb
                ON sl.{DATABASEKEYS.TRIP_SHARED_LINKS.TRIP_ID} = tb.{DATABASEKEYS.TRIPS.TRIP_ID}
                INNER JOIN {DATABASEKEYS.TABLES.USERDATA} as ud
                ON tb.{DATABASEKEYS.TRIPS.USER_ID} = ud.{DATABASEKEYS.USERDATA.USER_ID}
                WHERE sl.{DATABASEKEYS.TRIP_SHARED_LINKS.TOKEN} = %s;
                """,
                (token,),
            )
            con.commit()
            row = cur.fetchone()
            return dict(row) if row else None
        except ConnectionError as e:
            self.ErrorHandler.error("failed to connect to database", {str(e)})
            return None
        except Exception as e:
            self.ErrorHandler.error("failed to get all trip data from token", {str(e)})
            return None
        finally:
            self.close_db(conn=con)
