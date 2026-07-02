import json
import secrets
import uuid

from src.audit.userdata_audit import UserdataAudit
from src.database.database import Database
from src.database.database_keys import DATABASEKEYS
from src.database.s3.s3_client import ClientError
from src.database.s3.s3_dirs import AVATAR_DIR
from src.database.s3.s3_service import S3Sevice
from src.database.s3.s3_trip_contents import TripContentS3Service
from src.database.userdata_db_service import UserDataDataBaseService
from src.error_handler.error_handler import ErrorHandler
from src.mail.mail_service import CredentialEmailService
from src.repository.trip_repository import TripRepository
from src.repository.user_data_repository import UserDataRepository
from src.server_config.service.Etag.etag_services import UserdataEtag
from src.trip_service.trip_service import ms_to_timestamptz
from src.utils.cache.cache import Cache
from src.utils.exceptions import UserNotFound
from src.utils.handle_exception import handle_exception


def GENERATE_RANDOM_PENDING_TOKEN(user_id: str):

    return f"update_avatar::{user_id}::{uuid.uuid4()}"


def GENERATE_AVATAR_S3_KEY(user_id: str):
    return f"{AVATAR_DIR}user{user_id}_avatar.jpg"


def GENERATE_AVATAR_PATH(user_id: str):
    return f"user{user_id}_avatar.jpg"


def GENERATE_DELETE_USER_VERIFY_KEY(code: int):
    return f"delete_user_code:{code}"


class UserService:
    _instace = None
    _init = False

    def __new__(cls):
        if cls._instace is None:
            cls._instace = super().__new__(cls)
        return cls._instace

    def __init__(self):
        if self._init:
            return

        self.databaseService = Database()
        self.s3Service = S3Sevice()
        self.userDataEtagService = UserdataEtag()
        self.cacheService = Cache()
        self.UserDataBaseService = UserDataDataBaseService()
        self.ErrorHandler = ErrorHandler().logger("User Service")
        self.UserdataAudit = UserdataAudit()
        self.UserDataRepository = UserDataRepository()
        self.CredentialMailService = CredentialEmailService()
        self.TripRepository = TripRepository()
        self.TripContentS3Service = TripContentS3Service()
        self._init = True

    def get_user_data_from_database(
        self, user_id: int, client_etag: str | None
    ) -> tuple[dict, int]:
        try:
            assert user_id, "user_id empty"

            userdata_row = self.UserDataBaseService.get_user_data_by_id(user_id=user_id)
            # return false if username not exist
            if userdata_row is None:
                return {"code": "user_not_found"}, 500
            # get modified_time
            modified_time = userdata_row["modified_time"]
            # generate etag
            etag = self.userDataEtagService.generate_etag(
                user_id=user_id, modified_time=modified_time
            )

            if etag == client_etag:
                return {"code": "successfully", "message": "Not Change"}, 304
            # generate link for avatar
            avatar = userdata_row["avatar"]
            print(avatar)
            if avatar:
                avatar = self.s3Service.generate_temp_uri(key=avatar)
                userdata_row["avatar"] = avatar

            return (
                {"user_data": userdata_row, "code": "successfully", "etag": etag},
                200,
            )
        except AssertionError as ass:
            raise ValueError(str(ass))
        except Exception as e:
            self.ErrorHandler.error("failed at get userdata", {e})
            return {"code": "failed"}, 500

    def request_user_avatar_upload_presign_url(self, user_id: str):
        try:
            assert user_id, "user_id empty"

            path_key = f"{AVATAR_DIR}user{user_id}_avatar.jpg"
            # only except image
            content_type = "image/jpeg"
            # max size 5mb
            max_size = 5 * 1024 * 1024
            # key
            #
            presign_url = self.s3Service.generate_upload_url(
                key=path_key, content_type=content_type, max_size=max_size
            )
            if not presign_url:
                return {"code": "failed_to_generate_presign_url"}, 500

            token = GENERATE_RANDOM_PENDING_TOKEN(user_id=user_id)
            self.cacheService.set(key=token, time=300, data=path_key)

            return {
                "code": "successfully",
                "presign_url": presign_url,
                "pending_token": token,
            }, 201
        except AssertionError as e:
            return ({"code": "missing_inputs"}), 400
        except Exception as e:
            self.ErrorHandler.error("failed to requets presignurl", {e})
            return {"code": "failed"}, 500

    def process_update_user_avatar(
        self, user_id: str, pending_token: str, modified_time: str, ip_address: str
    ) -> tuple[dict, int]:
        MAX_RETRY = 2

        try:
            # get pending_token
            assert pending_token, "pending_token empty"
            assert user_id, "user_id epmty"

            path_key = self.cacheService.get(key=pending_token)

            if not path_key:
                return {"code": "request_not_found"}, 404

            # check if the object exists in the cloud
            if not self.s3Service.check_s3_object_exists(key=path_key):
                return {"code": "object not found"}, 404

            # update path in postgress
            format_time = ms_to_timestamptz(int(modified_time))
            for i in range(MAX_RETRY):
                if self.UserDataBaseService.update_user_avatar_and_modified_time(
                    user_id=user_id,
                    avatar_path=path_key,
                    modified_time=format_time,
                ):
                    break
            else:
                return {"code": "failed to update database"}, 500

            # delete from catch
            self.cacheService.delete(key=pending_token)
            # not strictly enforce, failed will be pass to error service
            self.UserdataAudit.change_user_avatar_audit(
                user_id=user_id,
                modified_time=format_time,
                ip_address=ip_address,
                old_value=path_key,
                new_value=path_key,
            )

            return {"code": "successfully"}, 200
        except ClientError as e:
            self.ErrorHandler.error("failed to reach s3", {e})
            return {"code": "failed_to_reach_s3_cloud"}, 500
        except AssertionError as e:
            return {"code": "missing_input", "message": str(e)}, 400
        except Exception as e:
            self.ErrorHandler.error("failed to requets presignurl", {str(e)})
            return {"code": "failed"}, 500

    @handle_exception("User Service", "request-delete-user")
    def request_delete_user(self, user_id):
        user_data = self.UserDataRepository.get_user_data(user_id=user_id)
        print("user_data", user_data)
        if not user_data:
            raise UserNotFound

        email = user_data.get("email")
        rand_code = secrets.randbelow(900000) + 100000
        verify_key = GENERATE_DELETE_USER_VERIFY_KEY(code=rand_code)
        # set verify key to cache with data field user id for validation on future step
        self.cacheService.set(
            key=verify_key, data=json.dumps({"user_id": user_id}), time=300
        )
        # send code to email
        self.CredentialMailService.send_email_confirmation_code(
            code=rand_code, recipient=email
        )
        return {"code": "successfully"}, 200

    @handle_exception("User Service", "delete user")
    def delete_user(self, code, user_id):
        # get and check verify code
        verify_key = GENERATE_DELETE_USER_VERIFY_KEY(code=code)
        raw_data_from_cache = self.cacheService.get(key=verify_key)
        if not raw_data_from_cache:
            return {"code": "invalid_code", "message": "invalid code"}, 400
        data_from_cache = json.loads(raw_data_from_cache)
        print(data_from_cache)
        # permission check
        if user_id != data_from_cache.get("user_id"):
            raise PermissionError("no permission to complete this action")

        # get trip list and to delete
        trip_list_need_to_delete = self.TripRepository.get_all_trip_data(
            user_id=user_id
        )
        print("reips", trip_list_need_to_delete)
        # since all related data have contrain with user id in userdata, delete the main will result in all data realated to user in other table to be deleted
        delete_from_database = self.UserDataRepository.delete_user(user_id=user_id)
        print(delete_from_database)

        if not delete_from_database:
            return {
                "code": "failed",
                "message": "Faild to delete data from database",
            }, 500
        # after successfully delete the user data
        # delete all media live in s3
        if trip_list_need_to_delete:
            for trip in trip_list_need_to_delete:
                trip_id = trip.get("trip_id")
                if not trip_id:
                    continue
                self.TripContentS3Service.delete_all_contents_in_trip(trip_id=trip_id)

        self.cacheService.delete(key=verify_key)
        return {"code": "successfully", "message": "successfully"}, 200
