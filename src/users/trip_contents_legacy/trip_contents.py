##
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


class UsersTripContentsService:
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


    @handle_exception("User Trip Content", "get all trip contents from trip")
    def get_all_content_card_from_trip_id(
        self, trip_id: str, request_id:int = None) -> tuple[list[dict], int]:
        # guard

        if not trip_id:
            raise ValueError("missing inputs")
        #  privacy checking
        self.TripPolicy.trip_permission_policy(request_id=request_id,trip_id=trip_id)
        # ------------------------------check cache------------------------------
        cache_key = GetTripContentsCacheKey(trip_id=trip_id)
        raw = self.CacheService.get(key=cache_key)
        if raw:
            contents = json.loads(raw)
            return {"code": "successfully", "content_cards": contents}, 200
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
