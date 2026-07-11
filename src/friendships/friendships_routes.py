from crypt import methods

from flask import blueprints, request
from flask.json import jsonify

from src.friendships.friendships_service import FriendShipsService
from src.server_config.service.smart_cast import smart_cast
from src.base.route_base import RouteBase
from src.utils.route_exception import route_exception


class FriendShipRoutes(RouteBase):
    _instance = None
    _init = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init:
            return
        super().__init__()
        self.bp = blueprints.Blueprint("FriendShipsRoutes", __name__)
        self.FriendShipsService = FriendShipsService()
        self._register_routes()
        self._init = True

    def _register_routes(self):
        self.bp.route("/friends", methods=["GET"])(
            self.get_friends
        )
        self.bp.route("/incoming-friend-requests", methods=["GET"])(self.get_incoming_friend_list)
        self.bp.route("/outcoming-friend-requests", methods=["GET"])(
            self.get_outcoming_friend_list
        )
        self.bp.route("/get-relationship/<target_user_id>", methods=["GET"])(
            self.get_relationship
        )
        self.bp.route("/accept-friend-request", methods=["PATCH"])(
            self.accept_friend_request
        )
        self.bp.route("/request-friend", methods=["POST"])(
            self.request_friend
        )
        self.bp.route("/delete-relationship", methods=["DELETE"])(
            self.delete_relationship
        )

    @route_exception(
        service="Friend Ships Route",
        endpoint="get-friends",
        unit="minute",
        unit_value=15,
        max_requests=300,
    )
    def get_friends(self):
        user_data_from_jwt, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401
        user_id = user_data_from_jwt.get("user_id")

        data, code = self.FriendShipsService.get_friends_list(
            user_id=user_id
        )
        return jsonify(data), code


    @route_exception(
        service="Friend Ships Route",
        endpoint="get-incoming-friend-list",
        unit="minute",
        unit_value=15,
        max_requests=300,
    )
    def get_incoming_friend_list(self):
        user_data_from_jwt, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401
        user_id = user_data_from_jwt.get("user_id")

        data, code = self.FriendShipsService.get_incoming_friend_requests(
            user_id=user_id
        )
        return jsonify(data), code


    @route_exception(
        service="Friend Ships Route",
        endpoint="get-outcoming-friend-list",
        unit="minute",
        unit_value=15,
        max_requests=300,
    )
    def get_outcoming_friend_list(self):
        user_data_from_jwt, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401
        user_id = user_data_from_jwt.get("user_id")

        data, code = self.FriendShipsService.get_outcoming_requests(
            user_id=user_id
        )
        return jsonify(data), code


    @route_exception(
        service="Friend Ships Route",
        endpoint="accept-friend-request",
        unit="minute",
        unit_value=15,
        max_requests=300,
    )
    def accept_friend_request(self):
        user_data_from_jwt, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401
        user_id = user_data_from_jwt.get("user_id")
        body = request.json
        target_user_id = body.get('target_user_id')
        if not target_user_id:
            raise ValueError('invalid user id')
        data, code = self.FriendShipsService.accept_friend_request(
            user_id=user_id,target_user_id=target_user_id
        )
        return jsonify(data), code

    @route_exception(
        service="Friend Ships Route",
        endpoint="request-friend",
        unit="minute",
        unit_value=15,
        max_requests=300,
    )
    def request_friend(self):
        user_data_from_jwt, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401
        user_id = user_data_from_jwt.get("user_id")
        body = request.json
        target_user_id = body.get('target_user_id')
        if not target_user_id:
            raise ValueError('invalid user id')
        data, code = self.FriendShipsService.request_friend(
            user_id=user_id,target_user_id=smart_cast(target_user_id)
        )
        return jsonify(data), code

    @route_exception(
        service="Friend Ships Route",
        endpoint="get-relationship",
        unit="minute",
        unit_value=15,
        max_requests=300,
    )
    def get_relationship(self,target_user_id):
        user_data_from_jwt, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401
        user_id = user_data_from_jwt.get("user_id")

        if not target_user_id:
            raise ValueError('invalid user id')
        data, code = self.FriendShipsService.get_relationship(
            user_id=user_id,target_user_id=smart_cast(target_user_id)
        )
        return jsonify(data), code

    @route_exception(
        service="Friend Ships Route",
        endpoint="delete-relationship",
        unit="minute",
        unit_value=15,
        max_requests=300,
    )
    def delete_relationship(self):
        user_data_from_jwt, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401
        user_id = user_data_from_jwt.get("user_id")
        body = request.json
        target_user_id = body.get('target_user_id')
        if not target_user_id:
            raise ValueError('invalid user id')
        data, code = self.FriendShipsService.delete_relationship(
            user_id=user_id,target_user_id=smart_cast(target_user_id)
        )
        return jsonify(data), code
