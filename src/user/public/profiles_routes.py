from crypt import methods
import json

from flask import Blueprint, jsonify, request

from src.base.route_base import RouteBase

from src.utils.route_exception import route_exception
from src.user.public.profiles import ProfilesService
from src.utils.cache.cache import Cache
from src.utils.cache.keys.cache_keys import GetUserDataCacheKey


class ProfilesRoute(RouteBase):
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
        self.bp = Blueprint("profiles", __name__)
        self.ProfilesService = ProfilesService()
        self.Cache = Cache()
        self._register_route()
        self._init = True

    def _register_route(self):

        self.bp.route("/profiles/<user_id>", methods=["GET"])(self.get_user_data)
        self.bp.route("/search/<keywords>", methods=["GET"])(self.search_user)



    @route_exception(
        service="Profiles Route",
        endpoint="get_user_data",
        unit="minute",
        unit_value=15,
        max_requests=300,
    )
    def get_user_data(self,user_id):

        user_data, error = self._get_authenticated_user()
        if error or not user_data:
            return jsonify(error), 401
        user_id_from_jwt = user_data.get("user_id")
        if not user_id_from_jwt:
            raise ValueError("Missing user_id in JWT")

        user_data, code = self.ProfilesService.get_user_data(target_user_id=user_id)

        return jsonify(user_data), code

    def search_user(self,keywords):
        user_data, error = self._get_authenticated_user()
        if error or not user_data:
            return jsonify(error), 401
        user_id_from_jwt = user_data.get("user_id")
        if not user_id_from_jwt:
            raise ValueError("Missing user_id in JWT")

        user_data, code = self.ProfilesService.search_for_user(keywords=keywords)

        return jsonify(user_data), code
