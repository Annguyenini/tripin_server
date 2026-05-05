from src.audit.userdata_audit import UserdataAudit
from src.database.database import Database
from src.database.database_keys import DATABASEKEYS
from src.database.s3.s3_dirs import AVATAR_DIR
from src.database.s3.s3_service import S3Sevice
from src.database.userdata_db_service import UserDataDataBaseService
from src.error_handler.error_handler import ErrorHandler
from src.server_config.service.cache import Cache
from src.server_config.service.Etag.auth_etag_service import AuthEtagService
from src.server_config.service.Etag.etag_services import UserdataEtag


class UserService:
    _instace = None
    _init = False

    def __new__(cls):
        if cls._instace:
            return cls._instace
        cls._instace = super().__new__(cls)

    def __init__(self):
        if self._init:
            return

        self.databaseService = Database()
        self.s3Service = S3Sevice()
        self.authEtagService = AuthEtagService()
        self.userDataEtagService = UserdataEtag()
        self.cacheService = Cache()
        self.UserDataBaseService = UserDataDataBaseService()
        self.ErrorHandler = ErrorHandler()
        self.UserdataAudit = UserdataAudit()
        self._init = True

    def get_user_data_from_database(
        self, user_id: int, client_etag: str | None
    ) -> tuple[dict, int]:
        try:
            # check etag in cache
            if not user_id:
                return {"code": "invalid_user_id"}, 404
            # generate etag key
            etag_key = self.userDataEtagService.generate_etag_key(user_id=user_id)
            # get etag from cache
            etag_from_cache = self.userDataEtagService._get_etag_from_cache(
                etag_key=etag_key
            )
            # return early when match
            if client_etag == etag_from_cache and client_etag:
                return {
                    "etag": client_etag,
                    "message": "Not Change",
                    "code": "successfully",
                }, 304
            # find userdata in database
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
            if avatar:
                avatar = self.s3Service.generate_temp_uri(key="avatar/" + avatar)
                userdata_row["avatar"] = avatar

            # put etag into cache
            self.userDataEtagService._set_etag_to_cache(etag_key=etag_key, etag=etag)

            return (
                {"user_data": userdata_row, "code": "successfully", "etag": etag},
                200,
            )
        except Exception as e:
            self.ErrorHandler.logger("Userdata").error("failed at get userdata", {e})
            return {}, 500

    def update_user_avartar(
        self, ip_address: str, user_id: int, image, modified_time: str
    ) -> tuple[dict, int]:
        # default path
        path = f"user{user_id}_avatar.jpg"
        s3key = AVATAR_DIR + path
        # upload to aws s3
        s3_status = self.s3Service.upload_media(path=s3key, data=image)
        if not s3_status:
            return {
                "status": False,
                "message": "Error Upload To Cloud",
                "code": "failed",
            }, 500

        # write default avatar path to db and return 500 if error ocurr
        # db_status = self.databaseService.update_db('tripin_auth.userdata','id',user_id,'avatar',path)

        con, cur = self.databaseService.connect_db()
        # update path, and modified time
        try:
            cur.execute(
                f"""
                UPDATE {DATABASEKEYS.TABLES.USERDATA}
                SET {DATABASEKEYS.USERDATA.AVATAR} = %s,
                {DATABASEKEYS.USERDATA.MODIFIED_TIME} =%s
                WHERE {DATABASEKEYS.USERDATA.USER_ID} = %s;""",
                (path, modified_time, user_id),
            )
            con.commit()
        except Exception as e:
            self.ErrorHandler.logger("User_data").error(
                "Failed to update user avatar to postges", {e}
            )
            return {
                "status": False,
                "message": "Error Upload To Database",
                "code": "failed",
            }, 500

        finally:
            self.databaseService.close_db(conn=con)
        # generate etag,
        etag_key = self.userDataEtagService.generate_etag_key(user_id=user_id)
        etag = self.userDataEtagService.generate_etag(
            user_id=user_id, modified_time=modified_time
        )
        # audit

        self.UserdataAudit.update_user_audit(
            user_id=user_id,
            modified_time=modified_time,
            action="change_avatar",
            old_value=path,
            new_value=path,
            ip_address=ip_address,
        )
        # put etag into cache
        self.userDataEtagService._set_etag_to_cache(etag_key=etag_key, etag=etag)
        return {
            "status": True,
            "message": "Successfully",
            "code": "successfully",
            "etag": etag,
        }, 200
