from flask import Blueprint, jsonify, request

from src.server_config.service.smart_cast import smart_cast
from src.base.route_base import RouteBase
from src.users.trips.trip import UsersTripService
from src.users.trip_contents.trip_contents import UsersTripContentsService

class UsersTripContentsRoutes(RouteBase):
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
        self.bp = Blueprint("userstripcontents", __name__)
        self._register_route()
        self.UsersTripContentsService = UsersTripContentsService()
        self._init = True

    def _register_route(self):
        self.bp.route("/trip-contents/<trip_id>", methods=["GET"])(self.get_user_trip_contents)

    def get_user_trip_contents(self,trip_id):
        if not trip_id:
            return {'code':'invalid input'},400
        user_data, error = self._get_authenticated_user()
        user_id = None
        if user_data:
            user_id = user_data.get('user_id')
        data,code = self.UsersTripContentsService.get_all_content_card_from_trip_id(trip_id=smart_cast(trip_id),request_id=user_id)
        return jsonify(data),code
        ## get trips with public/friend privacy
