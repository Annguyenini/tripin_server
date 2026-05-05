from flask import Blueprint, jsonify, request

from src.base.route_base import RouteBase
from src.database.database_keys import DATABASEKEYS
from src.database.s3.s3_dirs import AVATAR_DIR
from src.database.s3.s3_service import S3Sevice
from src.database.userdata_db_service import UserDataDataBaseService
from src.error_handler.error_handler import ErrorHandler
from src.token.tokenservice import TokenService
from src.user.user_service import UserService


class UserRoute(RouteBase):
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.bp = Blueprint("user", __name__)
        self.S3Service = S3Sevice()
        self.TokenService = TokenService()
        self.UserService = UserService()
        self.UserDataBaseService = UserDataDataBaseService()
        self.ErrorHandler = ErrorHandler()
        self._register_route()

    def _register_route(self):
        self.bp.route("/update-avatar", methods=["POST"])(self.update_profile_image)
        self.bp.route("/get-user-data", methods=["GET"])(self.get_user_data)

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
        except Exception as e:
            self.ErrorHandler.logger("Userdata").error(
                "Error at get userdata endpoint", {e}
            )
            return None, 500

    def update_profile_image(self):
        """update user avatar

        Returns:
            jsonify: json object , http code
        """
        # get token and verify token

        user_data, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401

        # get user data direcly from jwt
        user_id = user_data.get("user_id")
        ip_address = request.remote_addr
        if not user_id:
            raise ValueError("Missing user_id in JWT")
        # get image and return if not image
        image = request.files.get("image")
        modified_time = request.form.get("modified_time")
        if image is None:
            return jsonify({"message": "No Image Found", "code": "failed"}), 401

        # upload to s3 and return 401 if error occurr
        upload, code = self.UserService.update_user_avartar(
            user_id=user_id,
            image=image,
            modified_time=modified_time,
            ip_address=ip_address,
        )
        # return 200
        return jsonify(upload), code
