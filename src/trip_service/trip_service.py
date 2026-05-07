import json
import time
from datetime import datetime, timezone
from this import s

import psycopg2

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
from src.server_config.service.input_validation import InputValidation
from src.token.tokenservice import TokenService


def ms_to_timestamptz(ms: int) -> datetime:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


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
            self.ErrorHandler = ErrorHandler()
            self.UserDatabaseService = UserDataDataBaseService()
            self.AllTripEtagService = AllTripsDataEtag()
            self.TripEtagService = TripDataEtag()
            self._init = True

    def process_new_trip(
        self,
        user_id: str,
        trip_name: str,
        created_time: str,
        image=None,
    ) -> tuple[dict, int]:
        try:
            # check if user on an active trip
            is_on_a_trip = self.TripDatabaseService.get_current_trip_id_from_user(
                user_id=user_id
            )
            if is_on_a_trip is not None:
                return {
                    "code": "active_trip",
                    "Message": "Currently on an active trip!",
                }, 400

            ##return if exists trip name from user
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

            ##process to create new trip
            # pending
            format_time = ms_to_timestamptz(int(created_time))
            assert format_time is not None, "format time must not none"
            trip_id = self.TripDatabaseService.insert_new_trip(
                user_id=user_id,
                created_time=format_time,
                trip_name=trip_name,
            )
            if not trip_id:
                return {
                    "code": "server_failed",
                    "message": "Error occur while creating trip",
                }, 500
            image_path = f"trips/{trip_id}/cover.jpg"

            # callback to delete trip if cloud failed
            def callback():
                self.TripDatabaseService.delete_trip_by_trip_id(trip_id=trip_id)

            # if image
            if image:
                try:
                    if not self.s3_service.upload_media(path=image_path, data=image):
                        callback()
                        return {"code": "cloud_failed", "message": "Cloud Failed"}, 500
                    if not self.TripDatabaseService.update_trip_image_cover(
                        trip_id=trip_id, path=image_path
                    ):
                        callback()
                        return {"code": "cloud_failed", "message": "Cloud Failed"}, 500

                except Exception as e:
                    self.ErrorHandler.logger("trip service").error(
                        "Failed to upload trip image to cloud", {e}
                    )
                    callback()
                    return {"code": "cloud_failed", "message": "Cloud Failed"}, 500

            return {"code": "successfully", "trip_id": trip_id}, 200
        except AssertionError as e:
            return {
                "code": "server_failed",
                "message": "Error occur while creating trip",
            }, 500

    def end_a_trip(self, trip_id: str, user_id: str, ended_time: str):
        try:
            assert trip_id is not None, "Trip id is None"
            assert user_id is not None, "User id is None"
            assert ended_time is not None, "Ended time is None"

            trip_data = self.TripDatabaseService.get_trip_data_from_trip_id(
                trip_id=trip_id
            )
            # not found
            if not trip_data:
                return {"code": "trip_no_found"}, 400
            # already ended
            if not trip_data["active"]:
                return {"code": "trip_ended"}, 200
            # owner validation
            if not self.trip_owner_validation(user_id=user_id, trip_data=trip_data):
                return {"code": "no_permission"}, 403
            # update columns in database
            format_time = ms_to_timestamptz(int(ended_time))
            assert format_time is not None, "format time must not none"
            end_trip = self.TripDatabaseService.update_end_trip(
                trip_id=trip_id, ended_time=format_time
            )

            if not end_trip:
                return {"code": "failed_to_end_trip"}, 500

            return {"code": "successfully"}, 200
        except Exception as e:
            self.ErrorHandler.logger("trip service").error("Failed at end trip", {e})
            return {"code": "failed_to_end_trip"}, 500
        except AssertionError as e:
            return {"code": "failed_to_end_trip", "message": "missing params"}, 500

    def get_current_trip_id(self, user_id: str) -> tuple[dict, int]:
        current_trip_id = self.TripDatabaseService.get_current_trip_id_from_user(
            user_id=user_id
        )
        return ({"current_trip_id": current_trip_id}, 200)

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
        # fetch the etag from cache if match return
        etag_from_cache = self.TripEtagService._get_etag_from_cache(etag_key=etag_key)
        if client_etag == etag_from_cache and client_etag and etag_from_cache:
            return {}, 304

        # trip data from database
        trip_data_row = self.TripDatabaseService.get_trip_data_from_trip_id(
            trip_id=trip_id
        )
        # owner validation
        if not self.trip_owner_validation(user_id=user_id, trip_data=trip_data_row):
            return {"code": "no_permission"}, 403

        # if doesnt exist return nothing
        if trip_data_row is None:
            return {}, 400
        modified_time = trip_data_row["modified_time"]
        hour_bucket = int(time.time() // 3600)

        new_etag = self.TripEtagService.generate_etag(
            trip_id=trip_id, modified_time=modified_time, bucket_hour=hour_bucket
        )
        if client_etag == new_etag and client_etag:
            return {}, 304
        # set etag to redis
        self.TripEtagService._set_etag_to_cache(etag_key=etag_key, etag=new_etag)

        trip_data_row["created_time"] = (
            int(trip_data_row["created_time"].timestamp() * 1000)
            if trip_data_row["created_time"]
            else trip_data_row["created_time"]
        )
        trip_data_row["ended_time"] = (
            int(trip_data_row["ended_time"].timestamp() * 1000)
            if trip_data_row["ended_time"]
            else trip_data_row["ended_time"]
        )
        trip_data_row["image"] = (
            self.s3_service.generate_temp_uri(trip_data_row["image"])
            if trip_data_row["image"]
            else trip_data_row["image"]
        )
        trip_data_row["trip_id"] = trip_data_row["id"]
        return {"trip_data": trip_data_row, "etag": new_etag}, 200

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
        trip_data["image"] = self.s3_service.generate_temp_uri(key=media_path)

        return ({"trip_data": trip_data, "etag": new_etag}, 200)

    def get_all_trip_data(self, user_id, client_etag=None) -> tuple[dict, int]:
        try:
            # check etag from cache
            etag_key = self.AllTripEtagService.generate_etag_key(user_id=user_id)
            cache_etag = self.cache_service.get(etag_key)
            if client_etag == cache_etag and cache_etag:
                return {}, 304

            # get userdata
            # check etag that been generate
            userdata = self.UserDatabaseService.get_user_data_by_id(user_id=user_id)
            modified_time = userdata["modified_time"]
            # use bucket hour to force reset aws temp url
            bucket_hour = int(time.time() // 3600)
            # new etag
            etag = self.AllTripEtagService.generate_etag(
                user_id=user_id, modified_time=modified_time, bucket_hour=bucket_hour
            )

            if client_etag == etag and client_etag:
                return {}, 304

            # get trips data
            trip_data_row = self.TripDatabaseService.get_all_trips_from_user_id(
                user_id=user_id
            )
            # early return
            if not trip_data_row:
                return {"code": "empty", "message": "There are no trips!"}, 200

            trip_data_list = []
            # loop through, convert time, generate image for each trip
            for row in trip_data_row:
                default_time = row["created_time"]
                row["created_time"] = int(default_time.timestamp() * 1000)
                default_time_end = row["ended_time"]
                if default_time_end:
                    row["ended_time"] = int(default_time_end.timestamp() * 1000)

                default_image_path = row["image"]
                # print('image',default_image_path)
                if default_image_path:
                    row["image"] = self.s3_service.generate_temp_uri(default_image_path)
                row_dict = dict(row)
                row_dict["trip_id"] = row_dict["id"]
                trip_data_list.append(row_dict)

            # push etag to cache
            self.AllTripEtagService._set_etag_to_cache(etag_key=etag_key, etag=etag)
            return (
                {"all_trip_data": trip_data_list, "etag": etag},
                200,
            )
        except Exception as e:
            self.ErrorHandler.logger("trip").error("Failed at get all trips data", {e})
            return {}, 500

    def change_trip_data(
        self,
        new_trip_name: str,
        trip_id: str,
        user_id: str,
        modified_time: str,
        image=None,
    ) -> tuple[dict | None, int]:
        _changed_name = False
        # guard
        if not new_trip_name and not image or not user_id:
            return {}, 400
        # trip_data before change
        old_trip_data = self.TripDatabaseService.get_trip_data_from_trip_id(
            trip_id=trip_id
        )
        if not old_trip_data:
            return {"code": "trip_not_found"}, 400
        # trip_owner validation
        if not self.trip_owner_validation(user_id=user_id, trip_data=old_trip_data):
            return {"code": "no_permission"}, 403
        # if want to change trip name
        if new_trip_name:
            if not self.input_validation.trip_name_validation(trip_name=new_trip_name):
                return {"code": INPUT_ERROR.TRIP_NAME}, 400
            # check if new trip name samee with the old one
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
                        return {
                            "code": "failed_update_db",
                            "message": "Faild to update into database",
                        }, 500
                    _changed_name = True
            elif new_trip_name == old_trip_data["trip_name"]:
                return {
                    "code": "duplicate_trip_name",
                    "message": "Trip Name aldready exist!",
                }, 400
            pass

        # roll back
        def trip_name_rollback():
            if not _changed_name:
                return
            self.TripDatabaseService.update_trip_name(
                trip_id=trip_id, new_trip_name=old_trip_data["trip_name"]
            )

        if image:
            image_path = f"trips/{trip_id}/cover.jpg"
            # key will not be change
            upload_image = self.s3_service.upload_media(path=image_path, data=image)

            # upload new image to s3
            if not upload_image:
                trip_name_rollback()
                return {
                    "code": "failed_cloud",
                    "message": "Failed to upload to cloud",
                }, 500

            # update to postgres if not exist
            media_path_update = self.TripDatabaseService.update_trip_image_cover(
                trip_id=trip_id, path=image_path
            )
            if not media_path_update:
                trip_name_rollback()
                return {
                    "code": "failed_database",
                    "message": "Failed update image key",
                }, 500

        # update trip_data version
        update_trip_modified_time = self.TripDatabaseService.update_trip_modified_time(
            trip_id=trip_id, modified_time=modified_time
        )

        if not update_trip_modified_time:
            return {
                "code": "failed_update_version",
                "message": "Failed update trip data version",
            }, 500

        return {
            "code": "successfully",
            "message": "Successfully update trip data",
        }, 200

    def trip_owner_validation(self, user_id: str, trip_data: dict) -> bool:
        return trip_data["user_id"] == user_id
