from crypt import methods

from flask import blueprints, request
from flask.json import jsonify

from src.base.route_base import RouteBase
from src.trip_contents.trip_contents_service import TripContentsService


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
        self.bp.route("/get-all-contents", methods=["POST"])(self.get_add_trip_contents)
        self.bp.route("/sync", methods=["POST"])(self.sync_content_cards)
        self.bp.route("/request-presign-urls", methods=["POST"])(
            self.request_cloud_presign_url
        )

    def get_add_trip_contents(self):
        try:
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
        except Exception as e:
            print(e)
            return 500

    # def delete_content_card(self):
    #     user_data_from_jwt, error = self._get_authenticated_user()
    #     if error:
    #         return jsonify(error), 401

    #     card_data = request.form.get("card_data")
    #     trip_id = request.form.get("trip_id")
    #     media_type = request.form.get("media_type")
    #     insert, code = None, None
    #     if media_type == "photo":
    #         media = request.files.get("photo")
    #         insert, code = self.TripContentsService.insert_card(
    #             trip_id=trip_id, card_data=card_data, media=media
    #         )
    #     elif media_type == "video":
    #         media = request.files.get("video")
    #         insert, code = self.TripContentsService.insert_card(
    #             trip_id=trip_id, card_data=card_data, media=media
    #         )
    #     return jsonify(insert), code

    def sync_content_cards(self):
        user_data_from_jwt, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401
        data = request.json
        user_id = user_data_from_jwt.get("user_id")
        trip_id = data.get("trip_id")
        requests = data.get("requests")
        respond, code = self.TripContentsService.handle_sync(
            trip_id=trip_id, user_id=user_id, requests=requests
        )
        return jsonify(respond), code

    def request_cloud_presign_url(self):
        try:
            user_data_from_jwt, error = self._get_authenticated_user()
            if error:
                return jsonify(error), 401
            data = request.json
            user_id = user_data_from_jwt.get("user_id")
            content_cards = data.get("content_cards")
            trip_id = data.get("trip_id")
            print(content_cards)
            respond, code = self.TripContentsService.generate_presign_url_for_medias(
                user_id=user_id, trip_id=trip_id, content_cards=content_cards
            )
            return jsonify(respond), code
        except Exception as e:
            print(e)
            return 500
