import json
import time
from datetime import datetime, timezone
from typing import Any

from werkzeug.exceptions import Conflict

from src.repository.user_data_repository import UserDataRepository
from src.repository.friendships_repository import FriendShipsRepository
from src.database.database import Database
from src.database.s3.s3_service import S3Sevice
from src.database.trip_db_service import TripDatabaseService
from src.database.tripdata_db_service import TripDataBaseService
from src.database.userdata_db_service import UserDataDataBaseService
from src.error_handler.error_handler import ErrorHandler
from src.repository.trip_repository import TripRepository
from src.server_config.service.Etag.Etag import EtagService
from src.server_config.service.Etag.etag_services import AllTripsDataEtag, TripDataEtag
from src.server_config.service.Etag.trip_etag_service import TripEtagService
from src.server_config.service.input_validation import (
    InputValidation,
    TripInputValidation,
)
from src.token.tokenservice import TokenService
from src.utils.cache.cache import Cache
from src.utils.cache.keys.cache_keys import (
    GetTripDataCacheKey,
    GetUserTripsDataCacheKey,
    GetUsersTripDataCacheKey,
)
from src.utils.exceptions import TripNotFound, TripPermissionError
from src.utils.handle_exception import handle_exception


def ms_to_timestamptz(ms: int) -> datetime:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc) if ms else None


def timestamptz_to_ms(timestamp: datetime) -> int:
    return int(timestamp.timestamp() * 1000) if timestamp else None


class UsersTripService:
    _instance = None
    _init = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._init:
            self.token_service = TokenService()
            self.database_service = Database()
            self.trip_database_service = TripDatabaseService()
            self.TripDatabaseService = TripDataBaseService()
            self.s3_service = S3Sevice()
            self.etag_service = EtagService()
            self.trip_etag_service = TripEtagService()
            self.cache_service = Cache()
            self.input_validation = InputValidation()
            self.TripInputValidation = TripInputValidation()
            self.ErrorHandler = ErrorHandler()
            self.UserDatabaseService = UserDataDataBaseService()
            self.AllTripEtagService = AllTripsDataEtag()
            self.TripEtagService = TripDataEtag()
            self.TripRepository = TripRepository()
            self.FriendshipsRepository = FriendShipsRepository()
            self.UserDataRepository = UserDataRepository()
            self._init = True


    def _generate_all_trips_metadata_cache_key(self, user_id: str) -> str:
        return f"all_trips::user_id:{user_id}"

    def _generate_trip_data_cache_key(self, trip_id: str) -> str:
        return f"trip:{trip_id}"


    @handle_exception("Trip Service", "request trip data")
    def get_trip_data(
        self, user_id: str, trip_id: str, client_etag: str
    ) -> tuple[dict, int]:
        """_summary_

        Args:
            user_id (_type_): _description_
            etag (_type_): _description_
        """
        # -----------------------get from cache----------------------------
        cache_key = GetTripDataCacheKey(trip_id=trip_id)
        trip_data_row = None
        try:
            raw = self.cache_service.get(key=cache_key)
            if raw:
                trip_data_row = json.loads(raw)
        except json.JSONDecodeError as e:
            trip_data_row = None
        if trip_data_row:
            if not self.trip_owner_validation(user_id=user_id, trip_data=trip_data_row):
                raise TripPermissionError
            return {"code": "successfully", "trip_data": trip_data_row}, 200
        # ----------------------Cache miss----------------------------------
        # trip data from database
        trip_data_row = self.TripRepository.get_trip_data(trip_id=trip_id)
        # owner validation
        if not self.trip_owner_validation(user_id=user_id, trip_data=trip_data_row):
            raise TripPermissionError

        # if doesnt exist return nothing
        if trip_data_row is None or trip_data_row["event"] == "remove":
            raise TripNotFound

        # inject temp uri
        trip_data_row["image"] = (
            self.s3_service.generate_temp_uri(trip_data_row["image"])
            if trip_data_row["image"]
            else trip_data_row["image"]
        )
        # special key for app
        trip_data_row["trip_id"] = trip_data_row["id"]

        # ----------------put to cache---------------------
        self.cache_service.set(key=cache_key, data=json.dumps(trip_data_row), time=3600)
        return {"trip_data": trip_data_row}, 200


    @handle_exception("Trip service", "get trip list")
    def get_users_all_trip_data(self, target_user_id:int, user_id: int = None) -> tuple[dict, int]:


        #
        privacy_level = 'public'

        if user_id:
            user_id1,user_id2 = sorted([user_id,target_user_id])
            relationship = self.FriendshipsRepository.get_relationship(user_id1=user_id1,user_id2=user_id2)
            if relationship and relationship.get('status') =='FRIEND':
                privacy_level ='friend'

        # target
        target_user_data = self.UserDataRepository.get_user_data(user_id=target_user_id)
        trip_data_row = self.TripRepository.get_all_trip_data(user_id=target_user_id)

        # early return
        if not trip_data_row:
            return {"code": "empty", "message": "There are no trips!"}, 200

        trip_data_list = []
        # loop through, convert time, generate image for each trip
        #
        for row in trip_data_row:
            # FILTER
            privacy = row.get('privacy')

            if privacy =='private':
                continue
            elif privacy == 'friend' and privacy_level !='friend':

                continue
            # inject image
            default_image_path = row["image"]
            if default_image_path:
                row["image"] = self.s3_service.generate_temp_uri(default_image_path)
            row_dict = dict(row)


            allowed_data = {
                'created_time':row_dict.get('created_time'),
                'ended_time':row_dict.get('ended_time'),
                'trip_id':row_dict.get('id'),
                'image':row_dict.get('image'),
                'user_id':row_dict.get('trip_id'),
                'trip_name':row_dict.get('trip_name'),
                'author': target_user_data.get('user_name')}
            trip_data_list.append(allowed_data)
        return (
            {"all_trip_data": trip_data_list},
            200,
        )


    def trip_owner_validation(self, user_id: str, trip_data: dict) -> bool:
        return trip_data["user_id"] == user_id

    def _update_trip_modified_time(self, modified_time: datetime, trip_id: str) -> bool:
        return self.TripDatabaseService.update_trip_modified_time(
            trip_id=trip_id, modified_time=modified_time
        )

    def _invalidate_user_trip_list_cache(self, user_id: str):
        cache_key = self._generate_all_trips_metadata_cache_key(user_id=user_id)
        self.cache_service.delete(key=cache_key)
        self.TripRepository.invalidate_user_trips_cache(user_id=user_id)
        return

    def _invalidate_trip_cache(self, trip_id: str):
        cache_key = self._generate_trip_data_cache_key(trip_id=trip_id)
        self.cache_service.delete(key=cache_key)
        self.TripRepository.invalidate_trip_cache(trip_id=trip_id)
        return
