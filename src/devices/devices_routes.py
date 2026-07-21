from flask import Blueprint, jsonify, request

from src.devices.devices_service import DevicesService
from src.base.route_base import RouteBase
from src.utils.route_exception import route_exception
from src.types.device_types import Device


class DevicesRoutes(RouteBase):
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
        self.bp = Blueprint("devices", __name__)

        self.DevicesService = DevicesService()
        self._register_route()
        self._init = True

    def _register_route(self):

        self.bp.route("/insert-device", methods=["POST"])(self.insert_device)
    @route_exception(
        service="Devices Route",
        endpoint="insert-device",
        unit="minute",
        unit_value=15,
        max_requests=45,
    )
    def insert_device(self):
        user_data, error = self._get_authenticated_user()
        if error or not user_data:
            return jsonify(error), 401
        user_id_from_jwt = user_data.get("user_id")
        if not user_id_from_jwt:
            raise ValueError("Missing user_id in JWT")

        body = request.get_json()
        device = Device(user_id=user_id_from_jwt,device_id=body.get('device_id'),token=body.get('token'),platform=body.get('platform'),last_seen=body.get('last_seen'))

        data,code = self.DevicesService.insert_device(device=device)

        return data,code
