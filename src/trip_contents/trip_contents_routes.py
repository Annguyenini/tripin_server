from flask import blueprints, request
from flask.json import jsonify

from src.base.route_base import RouteBase
from src.trip_contents.trip_contents_service import TripContentsService


class TripContentRoute(RouteBase):
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
        self.bp = blueprints.Blueprint(__name__, "TripContentRoute")
        self.TripContentsService = TripContentsService()
        self._init = True

    def _register_routes(self):
        self.bp.route("/trip-contents/get-all-contents", methods=["POST"])

    def get_add_trip_contents(self):
        user_data_from_jwt, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401
        user_id = user_data_from_jwt.get("user_id")
        trip_data = request.json
        trip_id = trip_data.get("trip_id")
        data, code = self.TripContentsService.get_all_content_card_from_trip_id(
            trip_id=trip_id, user_id=user_id
        )
        return jsonify(code), code

    def delete_content_card(self):
        user_data_from_jwt, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401

        card_data = request.form.get("card_data")
        trip_id = request.form.get("trip_id")
        media_type = request.form.get("media_type")
        insert, code = None, None
        if media_type == "photo":
            media = request.files.get("photo")
            insert, code = self.TripContentsService.insert_card(
                trip_id=trip_id, card_data=card_data, media=media
            )
        elif media_type == "video":
            media = request.files.get("video")
            insert, code = self.TripContentsService.insert_card(
                trip_id=trip_id, card_data=card_data, media=media
            )
        return jsonify(insert), code

    def sync_content_card(self):
        user_data_from_jwt, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401

    def request_cloud_presign_url(self):
        user_data_from_jwt, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401
        urls = request.json
