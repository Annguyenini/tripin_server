from flask import Blueprint, jsonify, request

from src.server_config.service.smart_cast import smart_cast
from src.base.route_base import RouteBase
from src.users.trips.trip import UsersTripService

class UsersTripDataRoutes(RouteBase):
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
        self.bp = Blueprint("userstrips", __name__)
        self._register_route()
        self.UsersTripsService = UsersTripService()
        self._init = True

    def _register_route(self):
        self.bp.route("/trips/<target_user_id>", methods=["GET"])(self.get_user_trips)

    def get_user_trips(self,target_user_id):
        if not target_user_id:
            return {'code':'invalid input'},400
        user_data, error = self._get_authenticated_user()
        user_id = None
        if user_data:
            user_id = user_data.get('user_id')
        data,code = self.UsersTripsService.get_users_all_trip_data(target_user_id=smart_cast(target_user_id),user_id=user_id)
        return jsonify(data),code
        ## get trips with public/friend privacy
