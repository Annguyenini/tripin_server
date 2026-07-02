from crypt import methods

from flask import Blueprint, jsonify, request

from src.audit.userdata_audit import UserdataAudit
from src.base.route_base import RouteBase
from src.database.database_keys import DATABASEKEYS
from src.database.s3.s3_dirs import AVATAR_DIR
from src.database.s3.s3_service import S3Sevice
from src.database.userdata_db_service import UserDataDataBaseService
from src.error_handler.error_handler import ErrorHandler
from src.token.tokenservice import TokenService
from src.user.user_service import UserService
from src.utils.route_exception import route_exception


class UserRoute(RouteBase):
    _instance = None
    _init = False

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init:
            return
        super().__init__()
        self.bp = Blueprint("user", __name__)
        self.S3Service = S3Sevice()
        self.TokenService = TokenService()
        self.UserService = UserService()
        self.UserDataBaseService = UserDataDataBaseService()
        self.ErrorHandler = ErrorHandler()
        self.UserDataAudit = UserdataAudit()
        self._register_route()
        self._init = True

    def _register_route(self):
        self.bp.route("/request-update-avatar-presign-url", methods=["GET"])(
            self.request_update_avatar_presign_url
        )
        self.bp.route("/complete-update-avatar", methods=["POST"])(
            self.complete_update_user_avatar
        )
        self.bp.route("/get-user-data", methods=["GET"])(self.get_user_data)

        self.bp.route("/request-delete-user", methods=["POST"])(
            self.request_delete_user
        )
        self.bp.route("/delete-user", methods=["POST"])(self.delete_user)

    @route_exception(
        service="User Route",
        endpoint="get_user_data",
        unit="minute",
        unit_value=15,
        max_requests=300,
    )
    def get_user_data(self):
        try:
            user_data, error = self._get_authenticated_user()
            if error or not user_data:
                return jsonify(error), 401
            user_id_from_jwt = user_data.get("user_id")
            if not user_id_from_jwt:
                raise ValueError("Missing user_id in JWT")

            client_etag = request.headers.get("If-None-Match")

            user_data, code = self.UserService.get_user_data_from_database(
                user_id=user_id_from_jwt, client_etag=client_etag
            )

            return jsonify(user_data), code
        except ValueError as v:
            return {"code": "missing_inputs", "message": v}, code
        except Exception as e:
            self.ErrorHandler.logger("Userdata").error(
                "Error at get userdata endpoint", {e}
            )
            return {"code": "failed"}, 500

    @route_exception(
        service="User Route",
        endpoint="request_update_avatar_presign_url",
        unit="minute",
        unit_value=15,
        max_requests=45,
    )
    def request_update_avatar_presign_url(self):
        try:
            user_data = self._user_jwt_validation_policy()
            user_id = user_data.get("user_id")
            data, code = self.UserService.request_user_avatar_upload_presign_url(
                user_id=user_id
            )
            print(data, code)
            return jsonify(data), code
        except PermissionError as p:
            return {"code": "token_invalid"}, 401
        except Exception as e:
            self.ErrorHandler.logger("Userdata").error(
                "Error at request avatar presign url endpoint", {e}
            )
            return {"code": "server_failed"}, 500

    @route_exception(
        service="User Route",
        endpoint="complete_update_user_avatar",
        unit="minute",
        unit_value=15,
        max_requests=45,
    )
    def complete_update_user_avatar(self):
        try:
            user_data_from_jwt = self._user_jwt_validation_policy()
            user_id = user_data_from_jwt.get("user_id")
            user_data = request.json

            modified_time = user_data.get("modified_time")
            pending_token = user_data.get("pending_token")

            ip_address = self._get_request_ip_address()

            data, code = self.UserService.process_update_user_avatar(
                user_id=user_id,
                pending_token=pending_token,
                modified_time=modified_time,
                ip_address=ip_address,
            )
            print(data, code)

            return jsonify(data), code
        except PermissionError as p:
            return {"code": "token_invalid"}, 401
        except Exception as e:
            return {"code": "server_failed"}, 500

    @route_exception(
        service="User Route",
        endpoint="Request Delete User",
        unit="minute",
        unit_value=15,
        max_requests=15,
    )
    def request_delete_user(self):
        user_data_from_jwt = self._user_jwt_validation_policy()
        user_id = user_data_from_jwt.get("user_id")
        reponse, code = self.UserService.request_delete_user(user_id=user_id)
        return jsonify(reponse), code

    @route_exception(
        service="User Route",
        endpoint="Delete User",
        unit="minute",
        unit_value=15,
        max_requests=15,
    )
    def delete_user(self):
        user_data_from_jwt = self._user_jwt_validation_policy()
        user_id = user_data_from_jwt.get("user_id")
        user_data = request.json
        print(user_data)
        code = int(user_data.get("code"))
        print(code)

        if not code:
            raise ValueError("invalid code")
        response, statuscode = self.UserService.delete_user(code=code, user_id=user_id)
        return jsonify(response), statuscode
