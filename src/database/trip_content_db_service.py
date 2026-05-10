from error_handler.error_handler import ErrorHandler
from src.database.database import Database
from src.database.database_keys import DATABASEKEYS
from src.database.trip_db_service import TripDatabaseService


class TripContentsDatabaseService(TripDatabaseService):
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
        self.ErrorHandler = ErrorHandler()
        self._init = True

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
