import json
from datetime import datetime
from types import SimpleNamespace
from typing import Any

from flask.json import jsonify

from src.database.s3.s3_service import S3Sevice
from src.database.trip_content_db_service import TripContentsDatabaseService
from src.database.tripdata_db_service import TripDataBaseService
from src.database.view_trip_db_service import ViewTripDatabaseService
from src.error_handler.error_handler import ErrorHandler
from src.repository.trip_contents_repository import TripContentsRepository
from src.repository.trip_permission import TripPolicy
from src.repository.trip_repository import TripRepository
from src.token.tokenservice import TokenService
from src.trip_service.trip_service import (
    TripService,
    ms_to_timestamptz,
    timestamptz_to_ms,
)
from src.utils.cache.cache import Cache
from src.utils.cache.keys.cache_keys import GetTripContentsCacheKey
from src.utils.exceptions import TripNotFound
from src.utils.handle_exception import handle_exception


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
        self.ErrorHandler = ErrorHandler().logger("TripContentService")
        self.TokenService = TokenService()
        self.ViewTripDatabaseService = ViewTripDatabaseService()
        self.TripService = TripService()
        self.TripPolicy = TripPolicy()
        self.TripContentsRepository = TripContentsRepository()
        self.TripRepository = TripRepository()
        self.CacheService = Cache()
        self._init = True
        pass

    def _generate_content_key_s3(
        self, trip_id: str, timestamp_ms: int, content_type: str
    ):
        return f"trip{trip_id}_{timestamp_ms}.{'mp4' if content_type == 'video' else 'jpeg'}"

    def generate_presign_url_for_medias(
        self, trip_id: str, user_id: str, content_cards: list[str]
    ) -> tuple[list[str], int]:
        try:
            assert trip_id, "trip_id not found"
            assert user_id, "user id not found"
            if not self._trip_owner_validation(trip_id=trip_id, user_id=user_id):
                return {"code": "no_permission"}, 403
            for content_card in content_cards:
                media_path = self._generate_content_key_s3(
                    trip_id=trip_id,
                    timestamp_ms=content_card.get("time_stamp"),
                    content_type=content_card.get("media_type"),
                )
                content_type = f"{'video/mp4' if content_card.get('media_type') == 'video' else 'image/jpeg'}"
                content_card["presign_url"] = self.s3Service.generate_upload_url(
                    key=get_s3_media_path(trip_id=trip_id, media_path=media_path),
                    content_type=content_type,
                )

            return {
                "code": "successfully",
                "presign_urls": content_cards,
            }, 200
        except Exception as e:
            print(e)
            self.ErrorHandler.error("Failed to resolve generate url request", str(e))
            return {"code": "failed"}, 500

    @handle_exception("Trip Contents", "Handle sync")
    def handle_sync(
        self, trip_id: str, user_id: str, content_cards: list[Any]
    ) -> tuple[dict, int]:
        assert trip_id, "trip id is epmty"
        assert user_id, "user id is epmty"
        assert content_cards, "content_cards is empty"

        fail_requests = []
        for request in content_cards:
            # assume that request already sort from client
            if request.get("event") == "add":
                data, code = self._insert_card_to_database(
                    user_id=user_id, trip_id=trip_id, card_data=request
                )
                if code != 200:
                    fail_requests.append(request)
                # pass
            elif request.get("event") == "remove":
                data, code = self._delete_content_card(
                    card_data=request, trip_id=trip_id
                )
                # if code != 200:
                #     fail_requests.append(request)

        if fail_requests:
            return {"code": "requests_failed", "request": fail_requests}, 500

        # ---------------------------invalidate cache---------------------------
        self._invalid_cache(trip_id=trip_id)
        return {"code": "successfully"}, 200

    def _insert_card_to_database(
        self, user_id: str, trip_id: str, card_data: dict[Any]
    ) -> tuple[bool, dict]:
        """ """
        try:
            assert card_data, "Card data is empty"
            assert trip_id, "Trip id is empty"
            # ------card data--------
            time_stamp = card_data.get("time_stamp")
            format_time = ms_to_timestamptz(int(time_stamp))
            uuid = card_data.get("uuid")
            # ------media data ------
            media_type = card_data.get("media_type")

            media_path = self._generate_content_key_s3(
                trip_id=trip_id, timestamp_ms=time_stamp, content_type=media_type
            )
            media_id = card_data.get("media_id")

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

            # # update modified time
            # update_modified_time = self.TripDatabaseService.update_trip_modified_time(
            #     trip_id=trip_id, modified_time=format_time
            # )

            # if not update_modified_time:
            #     return {"code": "failed_to_update_modified_time"}, 502

            return {"code": "successfully"}, 200

        except AssertionError as ass:
            self.ErrorHandler.logger("trip contents service").error(
                "Failed to handler user request", {ass}
            )
            return {"code": "input_error"}, 400
        except Exception as e:
            self.ErrorHandler.logger("trip contents service").error(
                "Failed to handler user request", {e}
            )
            return {"code": "failed"}, 500

    def _delete_content_card(
        self,
        card_data: dict[Any],
        trip_id: int,
    ) -> bool | str:
        # remove from db,
        try:
            assert card_data, "card data is empty"
            assert trip_id, "trip_id is empty"

            modified_time = card_data.get("modified_time")
            format_time = ms_to_timestamptz(int(modified_time))
            assert format_time, "modified time is empty"

            uuid = card_data.get("uuid")
            assert uuid, "uuid is empty"

            # get exists data from database
            server_card_data = self.TripContentsDatabase.get_trip_content_cards(
                uuid=uuid, trip_id=trip_id
            )

            if not server_card_data:
                return {"code": "content card not found"}, 404
            # -----media -----
            media_path = server_card_data.get("media_path")
            media_type = server_card_data.get("media_type")
            # process to delete in cloud
            if media_path and (media_type == "photo" or media_type == "video"):
                s3_path = get_s3_media_path(trip_id=trip_id, media_path=media_path)
                delete_from_s3 = self.s3Service.delete_media(path=s3_path)
                if not delete_from_s3:
                    return {"code": "failed_to_delete_media_from_cloud"}, 500
            # if delete from cloud success process to delete in postgres
            delete_from_postgres = (
                self.TripContentsDatabase.remove_media_card_from_database(
                    uuid=uuid, trip_id=trip_id, modified_time=format_time
                )
            )

            if not delete_from_postgres:
                return {"code": "database failed"}, 500

            return {"code": "successfully"}, 200
        except AssertionError as e:
            return {"code": "inputs invalid"}, 400
        except Exception as e:
            return {"code": "failed"}, 500

    @handle_exception("Trip Content", "get all trip contents from trip")
    def get_all_content_card_from_trip_id(
        self, trip_id: str, user_id: str, client_hash: str = None
    ) -> tuple[list[dict], int]:
        # guard

        if not trip_id or not user_id:
            raise ValueError("missing inputs")
        #  owner validation
        self.TripPolicy.trip_permission_policy(user_id=user_id, trip_id=trip_id)
        # ------------------------------check cache------------------------------
        cache_key = GetTripContentsCacheKey(trip_id=trip_id)
        raw = self.CacheService.get(key=cache_key)
        if raw:
            contents = json.loads(raw)
            return {"code": "successfully", "content_cards": contents}, 200
        # ------------------------------cache miss---------------------------------
        # check hash
        server_hash = self.TripContentsDatabase.generate_contents_hash(trip_id=trip_id)
        if client_hash == server_hash and client_hash and server_hash:
            return {"code": "match"}, 304
        # ------------------------------get contents------------------------------
        # content cards
        contents = self.TripContentsRepository.get_trip_content(trip_id=trip_id)
        if contents is None:
            return {"code": "failed"}, 500

        # loop through to convert data
        for content in contents:
            if content["event"] == "remove":
                continue
            media_type = content.get("media_type")
            # if media type is photo or video, genrate temp uri
            if media_type == "photo" or media_type == "video":
                default_path = content["media_path"]
                media_path = self.s3Service.generate_temp_uri(
                    get_s3_media_path(trip_id=trip_id, media_path=default_path)
                )
                content["media_path"] = media_path

        # ----------------------------------put in cache--------------------------------
        self.CacheService.set(key=cache_key, time=3600, data=json.dumps(contents))
        return {"code": "successfully", "content_cards": contents}, 200

    @handle_exception("Trip Content", "get content version")
    def get_content_version(self, user_id: int, trip_id: int):
        """version are based on content last update time and total count"""
        last_update = 0
        trip_contents = self.TripContentsRepository.get_trip_content(trip_id=trip_id)
        for content in trip_contents:
            if content["modified_time"] > last_update:
                last_update = content["modified_time"]

        version = f"trip:{trip_id}::{last_update}::{len(trip_contents)}"
        return {"code": "successfully", "version": version}, 200

        pass

    # def get_current_trip_contents_version(self,trip_id:int):

    def _trip_owner_validation(self, trip_id: str, user_id: str):
        try:
            trip_data = self.TripRepository.get_trip_data(trip_id=trip_id)
            if not trip_data:
                return False
            return trip_data.get("user_id") == user_id
        except Exception as e:
            self.ErrorHandler.error("Failed to verify trip owner", {e})
            return False

    def requestTripContentsHash(self, user_id: str, trip_id: str):
        try:
            assert trip_id, "trip id is empty"
            assert user_id, "user id is empty"
            self.owner_validation_policy(user_id=user_id, trip_id=trip_id)
            hash = self.TripContentsDatabase.generate_contents_hash(trip_id=trip_id)
            if not hash:
                return {"code": "failed"}, 500
            return {"code": "successfully", "hash": hash}, 200
        except PermissionError as e:
            return {"code": "no_permission"}, 403
        except Exception as e:
            self.ErrorHandler.error("Failed to resolve hash request", {e})
            return {"code": "failed"}, 500

    def get_all_content_card_meta_data_from_trip_id(
        self, trip_id: str, user_id: str
    ) -> tuple[list[dict], int]:
        try:
            # guard
            assert trip_id, "trip id is empty"
            assert user_id, "user id is empty"

            #  owner validation
            self.TripPolicy.trip_permission_policy(user_id=user_id, trip_id=trip_id)

            # content cards
            contents = self.TripContentsDatabase.get_all_trip_content_cards(
                trip_id=trip_id
            )
            if contents is None:
                return {"code": "failed"}, 500

            # loop through to convert data

            if contents is None:
                return {"code": "failed to get trip contents metadata"}, 502
            return {"code": "successfully", "content_cards": contents}, 200
        except AssertionError as ass:
            return {"code": "missing_require_inputs"}, 402
        except PermissionError as e:
            return {"code": "no_permission"}, 403
        except Exception as e:
            self.ErrorHandler.error("failed to get get trip contents metadata", {e})
            return {"code": "failed"}, 502

    def owner_validation_policy(self, user_id: str, trip_id: str):
        if not self._trip_owner_validation(user_id=user_id, trip_id=trip_id):
            raise PermissionError("no_permission")

    def _invalid_cache(self, trip_id: int):
        cache_key = GetTripContentsCacheKey(trip_id=trip_id)
        self.CacheService.delete(key=cache_key)
        self.TripContentsRepository.invalid_trip_contents_cache(trip_id=trip_id)
