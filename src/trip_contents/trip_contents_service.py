from typing import Any

from database.s3.s3_service import S3Sevice
from database.trip_content_db_service import TripContentsDatabaseService
from database.tripdata_db_service import TripDataBaseService
from error_handler.error_handler import ErrorHandler
from trip_service.trip_service import ms_to_timestamptz


class TripContentsService:
    _instance = None
    _init = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._init:
            return

        self.TripContentsDatabase = TripContentsDatabaseService()
        self.s3Service = S3Sevice()
        self.TripDatabaseService = TripDataBaseService()
        self.ErrorHandler = ErrorHandler()
        self._init = True
        pass

    def insert_card(self, trip_id: str, card_data: dict[Any],media) -> tuple[dict, int]:
        try:
            assert card_data, "Card data is empty"
            assert trip_id, "Trip id is empty"
            # ------media data ------
            media_type = card_data.get("media_type")
            media_path = card_data.get("media_path")
            media_id = card_data.get("media_id")
            # ------card data--------
            time_stamp = card_data.get("time_stamp")
            format_time = ms_to_timestamptz(int(time_stamp))
            uuid = card_data.get("uuid")
            # -----location data ---
            altitude = card_data.get("altitude")
            latitude = card_data.get("latitude")
            longitude = card_data.get("longitude")
            speed = card_data.get("speed")
            heading = card_data.get("heading")
            city = card_data.get("city")
            region = card_data.get("region")
            country = card_data.get("country")
            iso_country_code = card_data.get("iso_country_code")
            # ---assert require data---
            assert time_stamp, "time stamp is empty"
            assert uuid, "uuid is empty"
            # insert media data first
            if media_path or media_type or media_id or media:
                assert media_path, "media path is empty"
                assert media_type, "media type is empty"
                assert media_id, "media id is empty"
                assert media,'media is empty'
                if media_type == 'photo' or media_type=='video'
                    s3_path = f"trips/{trip_id}/{media_path}"
                    insert_to_s3 = self.s3Service.upload_media(path=s3_path,media)
                    if not insert_to_s3:
                        return {'code':'failed at upload to cloud'},500
            # insert into postgres
            insert_to_database = self.TripContentsDatabase.insert_content_to_database(
                trip_id=trip_id,
                media_type=media_type,
                media_path=media_path,
                media_id=media_id,
                time_stamp=format_time,
                modified_time=format_time,
                uuid=uuid,
                altitude=altitude,
                latitude=latitude,
                longitude=longitude,
                speed=speed,
                heading=heading,
                city=city,
                region=region,
                country=country,
                iso_country_code=iso_country_code,
            )
            if not insert_to_database:
                return {"code": "failed_to_insert_to_database"}, 500

            # update modified time
            update_modified_time = self.TripDatabaseService.update_trip_modified_time(trip_id=trip_id,modified_time=format_time)

            if not update_modified_time:
                return {"code": "failed_to_update_modified_time"}, 500

            return {'code':'successfully'},200

        except AssertionError as ass:
            self.ErrorHandler.logger('trip contents service').error('Failed to handler user request',{ass})
            return {"code": "input_error"}, 400
        except Exception as e:
            self.ErrorHandler.logger('trip contents service').error('Failed to handler user request',{e})
            return {"code": "failed"}, 500
