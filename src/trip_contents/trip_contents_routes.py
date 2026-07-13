from crypt import methods

from flask import blueprints, request
from flask.json import jsonify

from src.base.route_base import RouteBase
from src.trip_contents.trip_contents_service import TripContentsService
from src.utils.route_exception import route_exception


class TripContentRoutes(RouteBase):
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
        self.bp = blueprints.Blueprint("TripContentRoute", __name__)
        self.TripContentsService = TripContentsService()
        self._register_routes()
        self._init = True

    def _register_routes(self):
        self.bp.route("/get-all-contents/<trip_id>", methods=["GET"])(
            self.get_trip_contents
        )
        self.bp.route("/sync", methods=["POST"])(self.sync_content_cards)
        self.bp.route("/request-presign-urls", methods=["POST"])(
            self.request_cloud_presign_url
        )
        self.bp.route("/request-trip-contents-hash", methods=["POST"])(
            self.request_trip_contents_hash
        )
        self.bp.route("/request-trip-contents-metadata", methods=["POST"])(
            self.request_trip_contents_metadata_for_sync
        )
        self.bp.route("/request-trip-contents-version/<trip_id>", methods=["GET"])(
            self.request_trip_contents_version
        )

    @route_exception(
        service="Trip Content Route",
        endpoint="get_trip_contents",
        unit="minute",
        unit_value=15,
        max_requests=500,
    )
    def get_trip_contents(self, trip_id: str):
        try:
            user_data_from_jwt, error = self._get_authenticated_user()
            if error:
                return jsonify(error), 401
            user_id = user_data_from_jwt.get("user_id")
            client_hash = request.headers.get("If-None-Match")
            # trip_data = request.json
            # trip_id = trip_data.get("trip_id")
            data, code = self.TripContentsService.get_all_content_card_from_trip_id(
                trip_id=trip_id, user_id=user_id, client_hash=client_hash
            )
            return jsonify(data), code
        except Exception as e:
            print(e)
            return 500

    @route_exception(
        service="Trip Content Route",
        endpoint="sync_content_cards",
        unit="minute",
        unit_value=15,
        max_requests=450,
    )
    def sync_content_cards(self):
        try:
            user_data_from_jwt, error = self._get_authenticated_user()
            if error:
                return jsonify(error), 401
            data = request.json
            user_id = user_data_from_jwt.get("user_id")
            trip_id = data.get("trip_id")
            content_cards = data.get("content_cards")
            respond, code = self.TripContentsService.handle_sync(
                trip_id=trip_id, user_id=user_id, content_cards=content_cards
            )
            return jsonify(respond), code
        except Exception as e:
            print(e)
            return 500

    @route_exception(
        service="Trip Content Route",
        endpoint="request_cloud_presign_url",
        unit="minute",
        unit_value=15,
        max_requests=450,
    )
    def request_cloud_presign_url(self):
        try:
            user_data_from_jwt, error = self._get_authenticated_user()
            if error:
                return jsonify(error), 401
            data = request.json
            user_id = user_data_from_jwt.get("user_id")
            content_cards = data.get("content_cards")
            trip_id = data.get("trip_id")
            respond, code = self.TripContentsService.generate_presign_url_for_medias(
                user_id=user_id, trip_id=trip_id, content_cards=content_cards
            )

            return jsonify(respond), code
        except Exception as e:
            print(e)
            return 500

    @route_exception(
        service="Trip Content Route",
        endpoint="request_trip_contents_hash",
        unit="minute",
        unit_value=15,
        max_requests=500,
    )
    def request_trip_contents_hash(self):
        try:
            user_data_from_jwt, error = self._get_authenticated_user()
            if error:
                return jsonify(error), 401
            data = request.json
            user_id = user_data_from_jwt.get("user_id")
            trip_id = data.get("trip_id")
            respond, code = self.TripContentsService.requestTripContentsHash(
                user_id=user_id, trip_id=trip_id
            )

            return jsonify(respond), code
        except Exception as e:
            print(e)
            return 500

    @route_exception(
        service="Trip Content Route",
        endpoint="request-trip-contents-metadata",
        unit="minute",
        unit_value=15,
        max_requests=500,
    )
    def request_trip_contents_metadata_for_sync(self):
        try:
            user_data_from_jwt, error = self._get_authenticated_user()
            if error:
                return jsonify(error), 401
            data = request.json
            user_id = user_data_from_jwt.get("user_id")
            trip_id = data.get("trip_id")
            respond, code = (
                self.TripContentsService.get_all_content_card_meta_data_from_trip_id(
                    user_id=user_id, trip_id=trip_id
                )
            )

            return jsonify(respond), code
        except Exception as e:
            print(e)
            return 500

    @route_exception(
        service="Trip Content Route",
        endpoint="request-trip-contents-metadata",
        unit="minute",
        unit_value=15,
        max_requests=500,
    )
    def request_trip_contents_version(self, trip_id):
        try:
            user_data_from_jwt, error = self._get_authenticated_user()
            if error:
                return jsonify(error), 401
            user_id = user_data_from_jwt.get("user_id")
            respond, code = self.TripContentsService.get_content_version(
                user_id=user_id, trip_id=int(trip_id)
            )

            return jsonify(respond), code
        except Exception as e:
            print(e)
            return 500
