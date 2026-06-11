import json
import time
from datetime import datetime, timezone
from typing import Any

from werkzeug.exceptions import Conflict

from src.database.database import Database
from src.database.database_keys import DATABASEKEYS
from src.database.s3.s3_dirs import TRIP_DIR
from src.database.s3.s3_service import S3Sevice
from src.database.trip_db_service import TripDatabaseService
from src.database.tripdata_db_service import TripDataBaseService
from src.database.userdata_db_service import UserDataDataBaseService
from src.error_code.error_code import INPUT_ERROR
from src.error_handler.error_handler import ErrorHandler
from src.server_config.service.cache import Cache
from src.server_config.service.Etag.Etag import EtagService
from src.server_config.service.Etag.etag_services import AllTripsDataEtag, TripDataEtag
from src.server_config.service.Etag.trip_etag_service import TripEtagService
from src.server_config.service.input_validation import (
    InputValidation,
    TripInputValidation,
)
from src.token.tokenservice import TokenService
from src.utils.exceptions import TripNotFound, TripPermissionError
from src.utils.handle_exception import handle_exception


def ms_to_timestamptz(ms: int) -> datetime:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc) if ms else None


def timestamptz_to_ms(timestamp: datetime) -> int:
    return int(timestamp.timestamp() * 1000) if timestamp else None


class TripService:
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
            self._init = True

    def _generate_trip_cover_upload_verification_token(self, trip_id: str) -> str:
        return f"trip_cover_upload::trip_id:{trip_id}"

    def _generate_trip_cover_aws_s3_path(self, trip_id: str) -> str:
        return f"trips/{trip_id}/cover.jpg"

    def _generate_all_trips_metadata_cache_key(self, user_id: str) -> str:
        return f"all_trips::user_id:{user_id}"

    def _generate_trip_data_cache_key(self, trip_id: str) -> str:
        return f"trip:{trip_id}::metadata"

    @handle_exception("Trip service", "Process new trip")
    def process_new_trip(
        self,
        user_id: str,
        trip_name: str,
        created_time: str,
        image: bool,
    ) -> tuple[dict, int]:

        # -------------------check if user on an active trip
        is_on_a_trip = self.TripDatabaseService.get_current_trip_id_from_user(
            user_id=user_id
        )
        if is_on_a_trip is not None:
            raise Conflict(
                description={
                    "code": "active_trip",
                    "message": "Currently on an active trip!",
                }
            )

        # -----------------------input validation----------------------
        self.TripInputValidation.trip_name_validation(trip_name=trip_name)
        format_time = ms_to_timestamptz(int(created_time))
        assert format_time and isinstance(format_time, datetime), (
            "format time is null or not format correctly"
        )

        ## ---------------------return if exists trip name from user
        exist_trip_name = (
            self.TripDatabaseService.get_trip_data_from_trip_name_and_user_id(
                user_id=user_id, trip_name=trip_name
            )
        )
        if exist_trip_name:
            return {
                "code": "exists_trip_name",
                "message": f"Trip name: {trip_name} already exist!",
            }, 400
        ## -----------------------process to create new trip
        # pending
        trip_id = self.TripDatabaseService.insert_new_trip(
            user_id=user_id,
            created_time=format_time,
            trip_name=trip_name,
        )
        if not trip_id:
            raise Exception("Error occur while creating trip")

        ##----------------------if there are image -----------------
        # genrate presign url and pandinf token
        image_path = self._generate_trip_cover_aws_s3_path(trip_id=trip_id)

        # if image
        presign_url = None
        pending_token = None
        if image:
            presign_url = self.s3_service.generate_upload_url(
                key=image_path, content_type="image/jpeg"
            )
            if not presign_url:
                raise Exception("failed to created presign presign url")
            ## ----------------------generate and store token--------
            #
            pending_token = self._generate_trip_cover_upload_verification_token(
                trip_id=trip_id
            )
            data_to_cache = json.dumps({"trip_id": trip_id, "image_path": image_path})
            self.cache_service.set(key=pending_token, data=data_to_cache, time=300)

        # ----------------------update trip modify time--------------------
        if not self._update_trip_modified_time(
            modified_time=format_time, trip_id=trip_id
        ):
            raise Exception("failed to update modified time")
        # return
        # ----------------------invalidate cache---------------------------
        self._invalidate_user_trip_list_cache(user_id=user_id)

        return {
            "code": "successfully",
            "trip_id": trip_id,
            "presign_url": presign_url if presign_url else None,
            "pending_token": pending_token,
        }, 201

    @handle_exception("Trip Service", "trip cover verification")
    def trip_cover_verification(
        self, pending_token: str, modified_time: str, user_id: str
    ) -> tuple[dict, int]:
        assert pending_token, "pending_token is null"
        format_time = ms_to_timestamptz(modified_time)
        assert format_time and isinstance(format_time, datetime), (
            "modified_time is empty or not formated correctly"
        )
        # ------------------get image path and validate the input --------
        data_from_cache = json.loads(self.cache_service.get(key=pending_token))
        if not data_from_cache:
            return {"code": "not_found", "message": "image path not found"}, 400
        trip_id = data_from_cache.get("trip_id")
        if trip_id is None:
            print(data_from_cache)
            raise ValueError("trip_id is none")
        image_path = self._generate_trip_cover_aws_s3_path(trip_id=trip_id)

        self.TripInputValidation.trip_image_validation(image_path=image_path)

        # -------------------find image in s3---------------------
        is_exists = self.s3_service.check_s3_object_exists(key=image_path)
        if not is_exists:
            return {"code", "not_found", "message", "Trip image not found"}, 500
        # --------------------update trip cover path in postgres-----------
        if not self.TripDatabaseService.update_trip_image_cover(
            trip_id=trip_id, path=image_path
        ):
            raise Exception("Fail to update trip image")
        # -----------------update trip modified time-------------
        if not self._update_trip_modified_time(
            modified_time=format_time, trip_id=trip_id
        ):
            raise Exception("failed to update modified time")

        #   -------------------delete pending token---------------
        self.cache_service.delete(key=pending_token)

        # ----------------------invalidate cache ----------------
        self._invalidate_user_trip_list_cache(user_id=user_id)
        self._invalidate_trip_cache(trip_id=trip_id)

        return {"code": "successfully", "message": "Successfully"}, 200

    @handle_exception("Trip Service", "end trip")
    def request_end_trip(self, trip_id: str, user_id: str, ended_time: str):
        assert trip_id is not None, "Trip id is None"
        assert user_id is not None, "User id is None"
        assert ended_time is not None, "Ended time is None"

        trip_data = self.TripDatabaseService.get_trip_data_from_trip_id(trip_id=trip_id)
        # not found
        if not trip_data:
            raise TripNotFound
        # ---------------------- already ended------------------------
        if not trip_data["active"]:
            return {"code": "successfully"}, 200
        # ----------------------owner validation----------------------
        if not self.trip_owner_validation(user_id=user_id, trip_data=trip_data):
            raise TripPermissionError
        # --------------------update columns in database-----------------
        format_time = ms_to_timestamptz(int(ended_time))
        assert format_time is not None, "format time must not none"
        # ----------------------end trip-----------------------
        end_trip = self.TripDatabaseService.update_end_trip(
            trip_id=trip_id, ended_time=format_time
        )

        if not end_trip:
            return {"code": "failed_to_end_trip"}, 500

        # -----------------------Invalidate cache--------------
        self._invalidate_user_trip_list_cache(user_id=user_id)
        self._invalidate_trip_cache(trip_id=trip_id)

        return {"code": "successfully"}, 200

    def get_current_trip_id(self, user_id: str) -> tuple[dict, int]:
        current_trip_id = self.TripDatabaseService.get_current_trip_id_from_user(
            user_id=user_id
        )
        return ({"current_trip_id": current_trip_id}, 200)

    @handle_exception("Trip Service", "request trip data")
    def get_trip_data(
        self, user_id: str, trip_id: str, client_etag: str
    ) -> tuple[dict, int]:
        """_summary_

        Args:
            user_id (_type_): _description_
            etag (_type_): _description_
        """
        # etag key
        etag_key = self.TripEtagService.generate_etag_key(trip_id=trip_id)
        # -----------------------get from cache----------------------------
        cache_key = self._generate_trip_data_cache_key(trip_id=trip_id)
        trip_data_row = None
        try:
            raw = self.cache_service.get(key=cache_key)
            if raw:
                trip_data_row = json.loads(raw)
        except json.JSONDecodeError as e:
            trip_data_row = None
        if trip_data_row:
            print(trip_data_row)

            if not self.trip_owner_validation(user_id=user_id, trip_data=trip_data_row):
                raise TripPermissionError
            return {"code": "successfully", "trip_data": trip_data_row}, 200
        # ----------------------Cache miss----------------------------------
        # trip data from database
        trip_data_row = self.TripDatabaseService.get_trip_data_from_trip_id(
            trip_id=trip_id
        )
        # owner validation
        if not self.trip_owner_validation(user_id=user_id, trip_data=trip_data_row):
            raise TripPermissionError

        # if doesnt exist return nothing
        if trip_data_row is None or trip_data_row["event"] == "remove":
            raise TripNotFound
        modified_time = trip_data_row["modified_time"]
        hour_bucket = int(time.time() // 3600)

        new_etag = self.TripEtagService.generate_etag(
            trip_id=trip_id, modified_time=modified_time, bucket_hour=hour_bucket
        )
        if client_etag == new_etag and client_etag:
            return {}, 304
        # set etag to redis
        self.TripEtagService._set_etag_to_cache(etag_key=etag_key, etag=new_etag)

        trip_data_row["created_time"] = timestamptz_to_ms(trip_data_row["created_time"])
        trip_data_row["ended_time"] = timestamptz_to_ms(trip_data_row["ended_time"])
        trip_data_row["content_modified_time"] = timestamptz_to_ms(
            trip_data_row["content_modified_time"]
        )
        trip_data_row["modified_time"] = timestamptz_to_ms(
            trip_data_row["modified_time"]
        )
        trip_data_row["image"] = (
            self.s3_service.generate_temp_uri(trip_data_row["image"])
            if trip_data_row["image"]
            else trip_data_row["image"]
        )

        trip_data_row["trip_id"] = trip_data_row["id"]

        # ----------------put to cache---------------------
        self.cache_service.set(key=cache_key, data=json.dumps(trip_data_row), time=3600)
        return {"trip_data": trip_data_row}, 200

    def get_trip_data_from_token(
        self, client_etag, token: str
    ) -> tuple[dict | None, int]:
        """_summary_

        Args:
            user_id (_type_): _description_
            etag (_type_): _description_
        """
        trip_data = self.TripDatabaseService.get_trip_data_by_shared_token(token=token)
        if not trip_data:
            return {}, 400

        trip_id = trip_data["trip_id"]
        # etag key
        etag_key = self.TripEtagService.generate_etag_key(trip_id=trip_id)
        # fetch the etag from cache if match return
        etag_from_cache = self.TripEtagService._get_etag_from_cache(etag_key=etag_key)
        if client_etag == etag_from_cache and client_etag and etag_from_cache:
            return None, 304

        # checking for etag based on hour bucket and data version
        modified_time = trip_data["modified_time"]
        hour_bucket = int(time.time() // 3600)
        new_etag = self.TripEtagService.generate_etag(
            trip_id=trip_id, modified_time=modified_time, bucket_hour=hour_bucket
        )
        if client_etag == new_etag:
            return {"etag": new_etag}, 304
        # set etag to redis
        self.TripEtagService._set_etag_to_cache(etag_key=etag_key, etag=new_etag)
        media_path = trip_data["image"]
        if media_path:
            trip_data["image"] = self.s3_service.generate_temp_uri(key=media_path)

        return ({"trip_data": trip_data, "etag": new_etag}, 200)

    @handle_exception("Trip service", "get trip list")
    def get_all_trip_data(
        self, user_id, want_images=False, client_etag=None
    ) -> tuple[dict, int]:
        # ------------------------------Etag-------------------------

        # check etag that been generate
        userdata = self.UserDatabaseService.get_user_data_by_id(user_id=user_id)
        trips_modified_time = userdata["trips_modified_time"]
        # use bucket hour to force reset aws temp url
        bucket_hour = int(time.time() // 3600)
        # new etag
        etag = self.AllTripEtagService.generate_etag(
            user_id=user_id,
            modified_time=trips_modified_time,
            bucket_hour=bucket_hour,
        )

        if client_etag == etag and client_etag:
            return {}, 304

        # -----------------------------Cache---------------------------
        # get trips data
        cache_key = self._generate_all_trips_metadata_cache_key(user_id=user_id)
        cache_raw = self.cache_service.get(key=cache_key)
        if cache_raw:
            try:
                cache_trips_list = json.loads(cache_raw)
                if cache_trips_list:
                    {"all_trip_data": cache_trips_list, "etag": etag}, 200
            except json.JSONDecodeError as e:
                print(e)
                pass
        # ----------------------------Cache miss-----------------------
        trip_data_row = self.TripDatabaseService.get_all_active_trips_from_user_id(
            user_id=user_id
        )
        # early return
        if not trip_data_row:
            return {"code": "empty", "message": "There are no trips!"}, 200

        trip_data_list = []
        # loop through, convert time, generate image for each trip
        #
        for row in trip_data_row:
            row["created_time"] = timestamptz_to_ms(row["created_time"])

            row["ended_time"] = timestamptz_to_ms(row["ended_time"])

            row["content_modified_time"] = timestamptz_to_ms(
                row["content_modified_time"]
            )
            row["modified_time"] = timestamptz_to_ms(row["modified_time"])

            if want_images:
                default_image_path = row["image"]
                # print('image',default_image_path)
                if default_image_path:
                    row["image"] = self.s3_service.generate_temp_uri(default_image_path)
            row_dict = dict(row)
            row_dict["trip_id"] = row_dict["id"]
            trip_data_list.append(row_dict)

        # ------------------------push data to cache-------------------------
        self.cache_service.set(
            key=cache_key, data=json.dumps(trip_data_list), time=3600
        )
        return (
            {"all_trip_data": trip_data_list, "etag": etag},
            200,
        )

    @handle_exception("Trip Service", "Modify trip data")
    def change_trip_data(
        self,
        new_trip_name: str,
        trip_id: str,
        user_id: str,
        modified_time: str,
        image: bool,
    ) -> tuple[dict | None, int]:

        assert user_id, "user_id is empty"
        assert new_trip_name or image, "Missing new trip name or image"
        format_time = ms_to_timestamptz(modified_time)
        assert format_time and isinstance(format_time, datetime), (
            "modified_time is empty or not formated correctly"
        )

        # --------------------- trip_data before change-----------------------
        old_trip_data = self.TripDatabaseService.get_trip_data_from_trip_id(
            trip_id=trip_id
        )
        if not old_trip_data:
            return {"code": "trip_not_found", "message": "Trip not found"}, 400
        # ----------------------owner validation----------------------------
        if not self.trip_owner_validation(user_id=user_id, trip_data=old_trip_data):
            raise TripPermissionError

        presign_url = None
        pending_token = None
        # ----------------------modify new trip---------------------------
        if new_trip_name:
            self.TripInputValidation.trip_name_validation(trip_name=new_trip_name)
            # check if new trip name same with the old one
            if new_trip_name != old_trip_data["trip_name"]:
                exist_trip_name = (
                    self.TripDatabaseService.get_trip_data_from_trip_name_and_user_id(
                        trip_name=new_trip_name, user_id=user_id
                    )
                )

                # check if user already have a trip that have the same name with new_name
                if not exist_trip_name:
                    # update to database
                    update_trip_name = self.TripDatabaseService.update_trip_name(
                        trip_id=trip_id, new_trip_name=new_trip_name
                    )

                    # if failed
                    if not update_trip_name:
                        raise Exception("Fail to update trip name")

                elif exist_trip_name:
                    raise Conflict(
                        description={
                            "code": "duplicate_trip_name",
                            "message": "Trip Name aldready exist!",
                        },
                    )
            elif new_trip_name == old_trip_data["trip_name"]:
                pass

        # -----------------------modify trip image------------------------
        if image:
            # image for s3
            image_path = self._generate_trip_cover_aws_s3_path(trip_id=trip_id)
            # presign url for s3
            presign_url = self.s3_service.generate_upload_url(
                key=image_path, content_type="image/jpeg", expiration=300
            )
            # pending token after upload to s3 and verify
            pending_token = self._generate_trip_cover_upload_verification_token(
                trip_id=trip_id
            )
            # --------------------------Cache token----------------------
            self.cache_service.set(
                key=pending_token, data=json.dumps({"trip_id": trip_id}), time=300
            )
        # -----------------------------Update modify time---------------------

        if not self._update_trip_modified_time(
            modified_time=format_time, trip_id=trip_id
        ):
            raise Exception("failed to update modified time")
        # -----------------------------invalidate cache----------------------
        self._invalidate_user_trip_list_cache(user_id=user_id)
        self._invalidate_trip_cache(trip_id=trip_id)
        # ------------------------------------------------------------
        return {
            "code": "successfully",
            "message": "successfully generate trip",
            "pending_token": pending_token,
            "presign_url": presign_url,
        }, 201

    @handle_exception("Trip Service", "remove trip handler")
    def remove_trip(
        self, user_id: str, trip_id: str, deleted_time: str
    ) -> tuple[dict[Any, Any], int]:
        # ghost delete, also didnt delete image cover from s3
        assert user_id, "user_id not found"
        assert trip_id, "trip_id not found"
        assert deleted_time, "deleted_time not found "
        # --------------------------get trip data----------------------
        trip_data = self.TripDatabaseService.get_trip_data_from_trip_id(trip_id=trip_id)
        assert trip_data, "trip_data not found"

        if not trip_data:
            raise TripNotFound

        if trip_data["event"] == "remove":
            return {
                "code": "Aldready_remove",
                "message": "trip aldready removed",
            }, 400
        # --------------------------owner validation-------------------
        owner_validation = self.trip_owner_validation(
            user_id=user_id, trip_data=trip_data
        )

        assert owner_validation, "no permission"
        if not owner_validation:
            raise TripPermissionError
        # --------------------------remove trip from postgres------------
        update_postgres = self.TripDatabaseService.remove_trip(trip_id=trip_id)
        if not update_postgres:
            return {
                "code": "failed_to_remove_from_server_database",
                "message": "Failed To Remove From Server Database",
            }, 500
        format_time = ms_to_timestamptz(int(deleted_time))
        assert format_time, "format time not found"

        # --------------------------update modified time-----------------
        update_trips_modified_time = (
            self.UserDatabaseService.update_trips_modified_time(
                user_id=user_id, modified_time=format_time
            )
        )

        if not update_trips_modified_time:
            return {"code": "failed_to_update_trips_modified_time"}, 500

        # ---------------------------invalidate cache-------------------
        all_trip_cache_key = self._generate_all_trips_metadata_cache_key(
            user_id=user_id
        )
        self.cache_service.delete(key=all_trip_cache_key)

        trip_cache_key = self._generate_trip_data_cache_key(trip_id=trip_id)
        self.cache_service.delete(key=trip_cache_key)

        # -------------------------------------------------------
        return {"code": "successfully"}, 200

    def trip_owner_validation(self, user_id: str, trip_data: dict) -> bool:
        return trip_data["user_id"] == user_id

    def _update_trip_modified_time(self, modified_time: datetime, trip_id: str) -> bool:
        return self.TripDatabaseService.update_trip_modified_time(
            trip_id=trip_id, modified_time=modified_time
        )

    def _invalidate_user_trip_list_cache(self, user_id: str):
        cache_key = self._generate_all_trips_metadata_cache_key(user_id=user_id)
        self.cache_service.delete(key=cache_key)
        return

    def _invalidate_trip_cache(self, trip_id: str):
        cache_key = self._generate_trip_data_cache_key(trip_id=trip_id)
        self.cache_service.delete(key=cache_key)
        return
