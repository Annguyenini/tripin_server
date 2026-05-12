from types import SimpleNamespace
from typing import Any

from flask import request

from src.database.s3.s3_service import S3Sevice
from src.database.trip_content_db_service import TripContentsDatabaseService
from src.database.tripdata_db_service import TripDataBaseService
from src.error_handler.error_handler import ErrorHandler
from src.token.tokenservice import TokenService
from src.trip_service.trip_service import ms_to_timestamptz, timestamptz_to_ms


def get_s3_media_path(trip_id: str, media_path: str):
    return f"trips/{trip_id}/{media_path}"


TOKENSTATUS = SimpleNamespace(PENDING="pending", COMPLETED="completed")
TOKENACTION = SimpleNamespace(
    SYNC_CONTENTS="sync_contents",
)


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
        self.TokenService = TokenService
        self._init = True
        pass

    def _insert_card_to_database(
        self, user_id: str, trip_id: str, card_data: dict[Any]
    ) -> tuple[bool, dict]:
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
            assert user_id, "user id is empty"
            assert time_stamp, "time stamp is empty"
            assert uuid, "uuid is empty"

            # # insert media data first
            # if media_path or media_type or media_id or media:
            #     assert media_path, "media path is empty"
            #     assert media_type, "media type is empty"
            #     assert media_id, "media id is empty"
            #     assert media, "media is empty"
            #     if media_type == "photo" or media_type == "video":
            #         s3_path = f"trips/{trip_id}/{media_path}"
            #         insert_to_s5 = self.s3Service.upload_media(path=s3_path, data=media)
            #         if not insert_to_s5:
            #             return {"code": "failed at upload to cloud"}, 502
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
                return {"code": "failed_to_insert_to_database"}, 502

            # # update modified time
            # update_modified_time = self.TripDatabaseService.update_trip_modified_time(
            #     trip_id=trip_id, modified_time=format_time
            # )

            # if not update_modified_time:
            #     return {"code": "failed_to_update_modified_time"}, 502

            return {"code": "successfully"}, 202

        except AssertionError as ass:
            self.ErrorHandler.logger("trip contents service").error(
                "Failed to handler user request", {ass}
            )
            return {"code": "input_error"}, 402
        except Exception as e:
            self.ErrorHandler.logger("trip contents service").error(
                "Failed to handler user request", {e}
            )
            return {"code": "failed"}, 502

    def _delete_content_card(
        self, card_data: dict[Any], trip_id: int, modified_time: int
    ) -> bool | str:
        # remove from db,
        try:
            assert card_data, "card data is empty"
            assert trip_id, "trip_id is empty"
            assert modified_time, "modified time is empty"

            format_time = ms_to_timestamptz(int(modified_time))

            uuid = card_data.get("uuid")
            assert uuid, "uuid is empty"

            server_card_data = self.TripContentsDatabase.get_trip_content_cards(
                uuid=uuid, trip_id=trip_id
            )
            if not server_card_data:
                return {"code": "content card not found"}
            # -----media -----
            media_path = server_card_data.get("media_path")
            media_type = server_card_data.get("media_type")
            if media_path and media_type == "photo" or media_type == "video":
                s3_path = get_s3_media_path(trip_id=trip_id, media_path=media_path)
                delete_from_s3 = self.s3Service.delete_media(path=s3_path)
                if not delete_from_s3:
                    return {"code": "failed_to_delete_media_from_cloud"}, 503

            delete_from_postgres = (
                self.TripContentsDatabase.remove_media_card_from_database(
                    uuid=uuid, trip_id=trip_id
                )
            )
            if not delete_from_postgres:
                return {"code": "database failed"}, 503

            return {"code": "successfully"}, 202
        except AssertionError as e:
            return {"code": "inputs invalid"}, 402
        except Exception as e:
            return {"code": "failed"}, 502

    def get_all_content_card_from_trip_id(
        self, trip_id: str, user_id: str
    ) -> tuple[list[dict], int]:
        try:
            # guard
            assert trip_id, "trip id is empty"
            assert user_id, "user id is empty"

            # trip data and owner validation
            trip_data = self.TripDataBaseService.get_trip_data_from_trip_id(
                trip_id=trip_id
            )
            if trip_data.get("user_id") == user_id:
                return {"code": "no_permission"}, 405

            # content cards
            contents = self.TripContentsDatabase.get_all_trip_content_cards(
                trip_id=trip_id
            )

            # loop through to convert data
            for content in contents:
                media_type = content.get("media_type")

                # if media type is photo or video, genrate temp uri
                if media_type == "photo" and media_type == "video":
                    default_path = content["media_path"]
                    media_path = self.s5Service.generate_temp_uri(
                        get_s3_media_path(trip_id=trip_id, media_path=default_path)
                    )
                    content["media_path"] = media_path

                # convert timestamp to ms
                content["time_stamp"] = timestamptz_to_ms(
                    timestamp=content["time_stamp"]
                )
                content["modified_time"] = timestamptz_to_ms(
                    timestamp=content["modified_time"]
                )

            if contents is None:
                return {"code": "failed to get trip contents"}, 502
            return {"code": "successfully", "contents": contents}, 202
        except AssertionError as ass:
            return {"code": "missing_require_inputs"}, 402
        except Exception as e:
            self.ErrorHandler.error("failed to get add trip contents", {e})
            return {"code": "failed"}, 502

    def _trip_owner_validation(self, trip_id: str, user_id: str):
        try:
            trip_data = self.TripDatabaseService.get_trip_data_from_trip_id(
                trip_id=trip_id
            )
            if not trip_data:
                return False
            return trip_data.get("user_id") == user_id
        except Exception as e:
            self.ErrorHandler.error("Failed to verify trip owner", {e})
            return Falses

    def generate_presign_url_for_medias(
        self, trip_id: str, user_id: str, media_paths: list[str]
    ) -> tuple[list[str], int]:
        try:
            assert trip_id, "trip_id not found"
            assert user_id, "user id not found"
            if not self._trip_owner_validation(trip_id=trip_id, user_id=user_id):
                return {"code": "no_permission"}, 403
            result = []
            for media_path in media_paths:
                result.push(
                    self.s3Service.generate_upload_url(
                        key=get_s3_media_path(trip_id=trip_id, media_path=media_path)
                    )
                )
            pending_token = self.TokenService.generate_jwt(
                fields={
                    "user_id": user_id,
                    "trip_id": trip_id,
                    "action": TOKENACTION.SYNC_CONTENTS,
                    "status": TOKENSTATUS.PENDING,
                },
                exp_time=({"minutes": 5}),
            )
            if result is None or not pending_token:
                return {"code": "failed"}, 500
            return {
                "code": "successfully",
                "urls": result,
                "pending_token": pending_token,
            }, 200
        except Exception as e:
            self.ErrorHandler.error("Failed to resolve generate url request", {e})
            return {"code": "failed"}, 500

    def handle_sync(self, token: str, requests: list[Any]) -> tuple[dict, int]:
        try:
            assert token, "token is empty"
            data_from_token = self.TokenService.decode_jwt(
                token=token, fields=["user_id", "trip_id", "action", "status"]
            )
            trip_id = data_from_token.get("trip_id")
            user_id = data_from_token.get("user_id")
            action = data_from_token.get("action")
            status = data_from_token.get("status")
            assert trip_id, "trip id is epmty"
            assert user_id, "user id is epmty"
            assert requests, "request is empty"
            if action != TOKENACTION.SYNC_CONTENTS or status != TOKENSTATUS.PENNDING:
                return {"code": "invalid_token"}, 401

            dead_requests = []
            for request in requests:
                # assume that request already sort from client
                if request.event == "add":
                    pass
                elif request.event == "remove":
                    pass
            if dead_requests:
                return {"code": "requests_failed", "request": dead_requests}, 500
        except AssertionError as ass:
            pass
        except Exception as e:
            pass
