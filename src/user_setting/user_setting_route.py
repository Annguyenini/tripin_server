from flask import Blueprint, jsonify, request

from src.audit.userdata_audit import UserdataAudit
from src.base.route_base import RouteBase
from src.error_handler.error_handler import ErrorHandler
from src.user_setting.user_setting_service import UserSettingsService
from src.utils.handle_exception import handle_exception
from src.utils.route_exception import route_exception
from types.device_types import Device


class UserSettingsRoutes(RouteBase):
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
        self.bp = Blueprint("user_settings", __name__)
        self.ErrorHandler = ErrorHandler()
        self.UserDataAudit = UserdataAudit()
        self.UserSettingsService = UserSettingsService()
        self._register_route()
        self._init = True

    def _register_route(self):
        self.bp.route("/user-settings", methods=["GET"])(self.get_user_settings)
        self.bp.route("/user-settings", methods=["PATCH"])(self.update_user_settings)

    @route_exception(
        service="User Setting Route",
        endpoint="get_user_settings",
        unit="minute",
        unit_value=15,
        max_requests=300,
    )
    def get_user_settings(self):
        user_data, error = self._get_authenticated_user()
        if error or not user_data:
            return jsonify(error), 401
        user_id_from_jwt = user_data.get("user_id")
        if not user_id_from_jwt:
            raise ValueError("Missing user_id in JWT")

        user_data, code = self.UserSettingsService.get_user_settings(
            user_id=user_id_from_jwt
        )

        return jsonify(user_data), code

    @route_exception(
        service="User Setting Route",
        endpoint="update_user_settings",
        unit="minute",
        unit_value=15,
        max_requests=45,
    )
    def update_user_settings(self):
        user_data, error = self._get_authenticated_user()
        if error or not user_data:
            return jsonify(error), 401
        user_id_from_jwt = user_data.get("user_id")
        if not user_id_from_jwt:
            raise ValueError("Missing user_id in JWT")

        settings = request.get_json()
        user_data, code = self.UserSettingsService.update_user_setting(
            user_id=user_id_from_jwt, settings=settings
        )

        return jsonify(user_data), code



    def insert_device(self):
        user_data, error = self._get_authenticated_user()
        if error or not user_data:
            return jsonify(error), 401
        user_id_from_jwt = user_data.get("user_id")
        if not user_id_from_jwt:
            raise ValueError("Missing user_id in JWT")

        body = request.get_json()
        device = Device(user_id=user_id_from_jwt,device_id=body.get('device_id'),token=body.get('token'),platform=body.get('platform'),last_seen=body.get('last_seen'))

        data,code = self.UserSettingsService.insert_device(device=device)

        return data,code
