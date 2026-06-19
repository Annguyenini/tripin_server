import uuid

from psycopg2.extensions import Boolean

from src.audit.userdata_audit import UserdataAudit
from src.database.database import Database
from src.database.database_keys import DATABASEKEYS
from src.database.s3.s3_client import ClientError
from src.database.s3.s3_dirs import AVATAR_DIR
from src.database.s3.s3_service import S3Sevice
from src.database.user_settings_db_service import UserSettingsDataBaseService
from src.database.userdata_db_service import UserDataDataBaseService
from src.error_handler.error_handler import ErrorHandler
from src.server_config.service.Etag.etag_services import UserdataEtag
from src.trip_service.trip_service import ms_to_timestamptz
from src.utils.cache.cache import Cache
from src.utils.handle_exception import handle_exception


class UserSettingsService:
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
        self.ErrorHandler = ErrorHandler().logger("User Setting `Service")
        self.UserdataAudit = UserdataAudit()
        self.UserSettingDatabaseService = UserSettingsDataBaseService()
        self._init = True

    @handle_exception("User Setting", "Get User Settings")
    def get_user_settings(self, user_id: int):
        if not user_id:
            raise ValueError("invalid user id")

        user_settings = self.UserSettingDatabaseService.get_user_settings_from_database(
            user_id=user_id
        )

        if not user_settings:
            return {"code": "failed", "message": "Fail to get setting"}, 500

        return {
            "code": "successfully",
            "message": "Successfully",
            "settings": dict(user_settings),
        }, 200

    @handle_exception("User Setting", "Update User Setting")
    def update_user_setting(self, user_id: int, settings: dict):
        allow_settings = ["has_seen_onboarding", "language"]
        clauses = ""
        columns = []
        values = []
        for set, val in settings.items():
            if set in allow_settings:
                columns.append(set + " = %s ")
                values.append(val)
        if not columns:
            raise ValueError("invalid inputs")
        clauses = ",".join(columns)
        values.append(user_id)

        update = self.UserSettingDatabaseService.update_user_settings(
            clauses=clauses, values=values
        )
        print(clauses, values)
        if not update:
            return {"code": "failed", "message": "Fail to update user settings"}, 500

        return {
            "code": "successfully",
            "message": "Successfully",
        }, 200
