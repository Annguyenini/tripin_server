from datetime import datetime

from src.database.database import Database
from src.database.database_keys import DATABASEKEYS
from src.database.trip_db_service import TripDatabaseService
from src.error_handler.error_handler import ErrorHandler
from src.trip_service.trip_service import timestamptz_to_ms


class TripContentsDatabaseService(Database):
    _instance = None
    _init = False

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init:
            return
        super().__init__()
        self.ErrorHandler = ErrorHandler().logger("Trip Contents Service")
        self._init = True

    def get_trip_content_cards(self, uuid: str, trip_id: str) -> dict:
        try:
            content = self.find_item_in_sql(
                table=DATABASEKEYS.TABLES.TRIP_CONTENT_CARDS,
                item=DATABASEKEYS.TRIP_CONTENT_CARDS.UUID,
                value=uuid,
                second_condition=True,
                second_item=DATABASEKEYS.TRIP_CONTENT_CARDS.TRIP_ID,
                second_value=trip_id,
            )
            return dict(content) if content else None
        except Exception as e:
            self.ErrorHandler.error("Faield to get trip content card", {e})
            return None

    def get_all_trip_add_content_cards(self, trip_id: str) -> list[dict] | None:
        try:
            contents = self.find_item_in_sql(
                table=DATABASEKEYS.TABLES.TRIP_CONTENT_CARDS,
                item=DATABASEKEYS.TRIP_CONTENT_CARDS.TRIP_ID,
                value=trip_id,
                return_option="fetchall",
                second_condition=True,
                second_item=DATABASEKEYS.TRIP_CONTENT_CARDS.EVENT,
                second_value="add",
                order_by=DATABASEKEYS.TRIP_CONTENT_CARDS.TIME_STAMP,
                order_type="DESC",
            )
            return [dict(content) for content in contents] if contents else []
        except Exception as e:
            self.ErrorHandler.error("Failed to get trip all trip content!")
            return None

    def get_all_trip_content_cards(self, trip_id: str) -> list[dict] | None:
        try:
            contents = self.find_item_in_sql(
                table=DATABASEKEYS.TABLES.TRIP_CONTENT_CARDS,
                item=DATABASEKEYS.TRIP_CONTENT_CARDS.TRIP_ID,
                value=trip_id,
                return_option="fetchall",
                order_by=DATABASEKEYS.TRIP_CONTENT_CARDS.CARD_ID,
                order_type="DESC",
            )
            return [dict(content) for content in contents] if contents else []
        except Exception as e:
            self.ErrorHandler.error("Failed to get trip all trip content!")
            return None

    def insert_content_to_database(
        self,
        trip_id: str,
        media_type: str,
        media_path: str,
        time_stamp: str,
        modified_time: str,
        media_id: str,
        uuid: str,
        altitude: float,
        latitude: float,
        longitude: float,
        speed: float,
        heading: float,
        city: str,
        region: str,
        country: str,
        iso_country_code: str,
    ):

        con, cur = self.connect_db()
        assert con and cur, "failed to connect to database"
        try:
            cur.execute(
                f"""
                INSERT INTO {DATABASEKEYS.TABLES.TRIP_CONTENT_CARDS}
                ({DATABASEKEYS.TRIP_CONTENT_CARDS.TRIP_ID},
                {DATABASEKEYS.TRIP_CONTENT_CARDS.MEDIA_TYPE},
                {DATABASEKEYS.TRIP_CONTENT_CARDS.MEDIA_PATH},
                {DATABASEKEYS.TRIP_CONTENT_CARDS.TIME_STAMP},
                {DATABASEKEYS.TRIP_CONTENT_CARDS.MODIFIED_TIME},
                {DATABASEKEYS.TRIP_CONTENT_CARDS.MEDIA_ID},
                {DATABASEKEYS.TRIP_CONTENT_CARDS.UUID},
                {DATABASEKEYS.TRIP_CONTENT_CARDS.ALTITUDE},
                {DATABASEKEYS.TRIP_CONTENT_CARDS.LATITUDE},
                {DATABASEKEYS.TRIP_CONTENT_CARDS.LONGITUDE},
                {DATABASEKEYS.TRIP_CONTENT_CARDS.SPEED},
                {DATABASEKEYS.TRIP_CONTENT_CARDS.HEADING},
                {DATABASEKEYS.TRIP_CONTENT_CARDS.CITY},
                {DATABASEKEYS.TRIP_CONTENT_CARDS.REGION},
                {DATABASEKEYS.TRIP_CONTENT_CARDS.COUNTRY},
                {DATABASEKEYS.TRIP_CONTENT_CARDS.ISO_COUNTRY_CODE})
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    trip_id,
                    media_type,
                    media_path,
                    time_stamp,
                    modified_time,
                    media_id,
                    uuid,
                    altitude,
                    latitude,
                    longitude,
                    speed,
                    heading,
                    city,
                    region,
                    country,
                    iso_country_code,
                ),
            )
            con.commit()
            return True if cur.rowcount >= 1 else False
        except Exception as e:
            self.ErrorHandler.logger("trip content database").error(
                "Failed to insert content card", {e}
            )
            return False
        finally:
            self.close_db(conn=con)
        pass

    def remove_media_card_from_database(
        self, uuid: str, trip_id: str, modified_time: datetime
    ) -> bool:
        """
        change event flag to 'remove'
        """
        con, cur = self.connect_db()
        try:
            cur.execute(
                f"""
                UPDATE {DATABASEKEYS.TABLES.TRIP_CONTENT_CARDS}
                SET {DATABASEKEYS.TRIP_CONTENT_CARDS.EVENT} = %s,
                {DATABASEKEYS.TRIP_CONTENT_CARDS.MODIFIED_TIME} =%s
                WHERE {DATABASEKEYS.TRIP_CONTENT_CARDS.UUID} =%s
                AND {DATABASEKEYS.TRIP_CONTENT_CARDS.TRIP_ID} =%s
                """,
                ("remove", modified_time, uuid, trip_id),
            )
            con.commit()
            return True if cur.rowcount >= 1 else False
        except Exception as e:
            self.ErrorHandler.logger("trip content database").error(
                "Failed to remove content card", {e}
            )
            return False
        finally:
            self.close_db(conn=con)

    def generate_contents_hash(self, trip_id: int):
        con, cur = None, None
        try:
            con, cur = self.connect_db()
            cur.execute(
                f"""
                        SELECT COUNT(*), MAX({DATABASEKEYS.TRIP_CONTENT_CARDS.MODIFIED_TIME})
                        FROM {DATABASEKEYS.TABLES.TRIP_CONTENT_CARDS}
                        WHERE {DATABASEKEYS.TRIP_CONTENT_CARDS.TRIP_ID} = %s
                        """,
                (trip_id,),
            )
            count, max = cur.fetchone()
            con.commit()

            return f"{count}:{timestamptz_to_ms(max) if max else 0}"
        except Exception as e:
            self.ErrorHandler.logger("TripDataBase").error(
                "Failed to get trip meida max", body=e
            )
            return None
        finally:
            if con:
                self.close_db(conn=con)
