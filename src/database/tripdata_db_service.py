from datetime import datetime, timezone

from src.database.database import Database
from src.database.database_keys import DATABASEKEYS
from src.error_handler.error_handler import ErrorHandler


class TripDataBaseService(Database):
    _instance = None
    _init = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init:
            return
        self.ErrorHandler = ErrorHandler()
        super().__init__()
        self._init = True

    def get_all_trips_from_user_id(self, user_id: str) -> list[dict] | None:
        userdata = self.find_item_in_sql(
            table=DATABASEKEYS.TABLES.TRIPS,
            item=DATABASEKEYS.TRIPS.USER_ID,
            value=user_id,
            second_condition=True,
            second_item=DATABASEKEYS.TRIPS.EVENT,
            second_value="add",
            return_option="fetchall",
            order_by=DATABASEKEYS.TRIPS.TRIP_ID,
            order_type="DESC",
        )
        return [dict(user) for user in userdata] if userdata else None

    def get_trip_data_from_trip_id(self, trip_id: str) -> dict | None:
        trip_data = self.find_item_in_sql(
            table=DATABASEKEYS.TABLES.TRIPS,
            item=DATABASEKEYS.TRIPS.TRIP_ID,
            value=trip_id,
        )
        return dict(trip_data) if trip_data else None

    def get_trip_data_from_trip_name_and_user_id(
        self, trip_name: str, user_id: str
    ) -> dict | None:
        trip_data = self.find_item_in_sql(
            table=DATABASEKEYS.TABLES.TRIPS,
            item=DATABASEKEYS.TRIPS.TRIP_NAME,
            value=trip_name,
            second_condition=True,
            second_item=DATABASEKEYS.TRIPS.USER_ID,
            second_value=user_id,
        )
        return dict(trip_data) if trip_data else None

    def update_trip_name(self, new_trip_name: str, trip_id: str) -> bool:
        return self.update_db(
            table=DATABASEKEYS.TABLES.TRIPS,
            item=DATABASEKEYS.TRIPS.TRIP_ID,
            value=trip_id,
            item_to_update=DATABASEKEYS.TRIPS.TRIP_NAME,
            value_to_update=new_trip_name,
        )

    def update_trip_image_cover(self, trip_id: str, path: str) -> bool:
        return self.update_db(
            table=DATABASEKEYS.TABLES.TRIPS,
            item=DATABASEKEYS.TRIPS.TRIP_ID,
            value=trip_id,
            item_to_update=DATABASEKEYS.TRIPS.IMAGE_KEY,
            value_to_update=path,
        )

    def update_trip_modified_time(self, trip_id: str, modified_time: str) -> bool:
        return self.update_db(
            table=DATABASEKEYS.TABLES.TRIPS,
            item=DATABASEKEYS.TRIPS.TRIP_ID,
            value=trip_id,
            item_to_update=DATABASEKEYS.TRIPS.MODIFIED_TIME,
            value_to_update=modified_time,
        )

    def update_trip_privacy(self, trip_id: str, privacy: str) -> bool:
        return self.update_db(
            table=DATABASEKEYS.TABLES.TRIPS,
            item=DATABASEKEYS.TRIPS.TRIP_ID,
            value=trip_id,
            item_to_update=DATABASEKEYS.TRIPS.PRIVACY,
            value_to_update=privacy,
        )

    def remove_trip(self, trip_id: str) -> bool:
        return self.update_db(
            table=DATABASEKEYS.TABLES.TRIPS,
            item=DATABASEKEYS.TRIPS.TRIP_ID,
            value=trip_id,
            item_to_update=DATABASEKEYS.TRIPS.EVENT,
            value_to_update="remove",
        )

    def get_current_trip_id_from_user(self, user_id: str) -> str | None:
        current_trip = self.find_item_in_sql(
            table=DATABASEKEYS.TABLES.TRIPS,
            item=DATABASEKEYS.TRIPS.USER_ID,
            value=user_id,
            second_condition=True,
            second_item=DATABASEKEYS.TRIPS.ACTIVE,
            second_value=True,
        )
        return current_trip["id"] if current_trip else None

    def insert_new_trip(
        self,
        user_id: str,
        created_time: int,
        trip_name: str,
        privacy: str = 'private'
    ) -> str | None:
        con, cur = self.connect_db()
        try:
            cur.execute(
                f"""INSERT INTO {DATABASEKEYS.TABLES.TRIPS}
                ({DATABASEKEYS.TRIPS.USER_ID},
                {DATABASEKEYS.TRIPS.TRIP_NAME},
                {DATABASEKEYS.TRIPS.CREATED_TIME},
                {DATABASEKEYS.TRIPS.ACTIVE},
                {DATABASEKEYS.TRIPS.MODIFIED_TIME},
                {DATABASEKEYS.TRIPS.PRIVACY}) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id""",
                (user_id, trip_name, created_time, True, created_time, privacy),
            )
            trip_id = cur.fetchone()["id"]
            con.commit()
            if cur.rowcount >= 1:
                return trip_id
        except Exception as e:
            self.ErrorHandler.logger("TripDataBase").error(
                "Failed to insert to database", body=e
            )
            return None
        finally:
            if con:
                self.close_db(conn=con)

    def get_trip_data_by_shared_token(self, token: str) -> dict | None:
        try:
            con, cur = self.connect_db()
            cur.execute(
                f"""SELECT
                        {DATABASEKEYS.TABLES.TRIP_SHARED_LINKS}.*,
                        {DATABASEKEYS.TABLES.TRIPS}.*,
                        {DATABASEKEYS.TABLES.USERDATA}.display_name
                        FROM {DATABASEKEYS.TABLES.TRIP_SHARED_LINKS}
                        INNER JOIN {DATABASEKEYS.TABLES.TRIPS}
                        ON {DATABASEKEYS.TRIP_SHARED_LINKS.TRIP_ID} = {DATABASEKEYS.TABLES.TRIPS}.id
                        INNER JOIN {DATABASEKEYS.TABLES.USERDATA}
                        ON {DATABASEKEYS.TABLES.TRIPS}.user_id = {DATABASEKEYS.TABLES.USERDATA}.id
                        WHERE {DATABASEKEYS.TRIP_SHARED_LINKS.TOKEN} = %s""",
                (token,),
            )

            row = cur.fetchone()
            con.commit()
            return dict(row) if row else None
        except Exception as e:
            self.ErrorHandler.logger("TripDataBase").error(
                "Failed to update trip version", body=e
            )
            return None
        finally:
            self.close_db(conn=con)

    def delete_trip_by_trip_id(self, trip_id: str) -> bool:
        con, cur = self.connect_db()

        try:
            cur.execute(
                f"""DELETE FROM {DATABASEKEYS.TABLES.TRIPS} WHERE {DATABASEKEYS.TRIPS.TRIP_ID} = %s""",
                (trip_id),
            )
            trip_id = cur.fetchone()["id"]
            con.commit()
            return True if cur.rowcount >= 1 else False

        except Exception as e:
            self.ErrorHandler.logger("TripDataBase").error(
                "Failed to delete to database", body=e
            )
            return False
        finally:
            self.close_db(conn=con)

    def update_end_trip(self, trip_id: str, ended_time: datetime):
        con, cur = self.connect_db()
        try:
            cur.execute(
                f"""
                UPDATE {DATABASEKEYS.TABLES.TRIPS} SET {DATABASEKEYS.TRIPS.ENDED_TIME} = %s, {DATABASEKEYS.TRIPS.ACTIVE} = %s WHERE {DATABASEKEYS.TRIPS.TRIP_ID} = %s
                """,
                (
                    ended_time,
                    False,
                    trip_id,
                ),
            )
            con.commit()
            return True if cur.rowcount >= 1 else False
        except Exception as e:
            self.ErrorHandler.logger("Trip Database").error("Failed at end trip", {e})
            return False
        finally:
            self.close_db(conn=con)
