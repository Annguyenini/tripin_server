import json
from crypt import methods

from flask import Blueprint, jsonify, request

from src.base.route_base import RouteBase
from src.database.s3.s3_dirs import TRIP_DIR
from src.database.s3.s3_service import S3Sevice
from src.database.trip_db_service import TripDatabaseService
from src.geo.geo_service import GeoService
from src.server_config.service.cache import Cache
from src.token.tokenservice import TokenService
from src.trip_service.trip_contents.trip_contents_service import TripContentService
from src.trip_service.trip_service import TripService


class TripRoute(RouteBase):
    _instance = None
    _init = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init:
            return
        super().__init__()
        self.bp = Blueprint("trip", __name__)
        self.token_service = TokenService()
        self.trip_service = TripService()
        self.trip_content_service = TripContentService()
        self.trip_s3 = S3Sevice()
        self.geo_service = GeoService()
        self.cache_service = Cache()
        self.trip_database_service = TripDatabaseService()
        self._init = True
        self._register_route()

    def _register_route(self):
        self.bp.route("/new-trip", methods=["POST"])(self.request_new_trip)
        self.bp.route("/all-trips/full", methods=["GET"])(self.request_all_trips_data)
        self.bp.route("/current-trip-id", methods=["GET"])(self.request_current_trip_id)
        self.bp.route("/end-trip", methods=["POST"])(self.end_trip)
        self.bp.route("/trip", methods=["POST"])(self.request_trip_data)
        self.bp.route("/trip-by-token/<token>", methods=["GET"])(
            self.request_trip_data_by_shared_links
        )
        self.bp.route("/modify-trip-data", methods=["POST"])(self.change_trip_data)
        self.bp.route("/trip", methods=["DELETE"])(self.request_remove_trip)

    ## request new trip
    def request_new_trip(self):
        """take in user data to process new trip

        Returns:
            status: html status, message
        """
        # Ptoken = request.headers.get("Authorization")
        # token=Ptoken.replace("Bearer ","")

        # ##verify token
        # valid_token,Tmessage,code = self.token_service.jwt_verify(token)
        # ##return if invalid token
        # if not valid_token:
        #     print(code)
        #     return jsonify ({"message":Tmessage,"code":code}), 401
        user_data, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401
        ##decode jwt to get userdatas
        user_id = user_data.get("user_id")
        trip_name = request.form.get("trip_name")
        created_time = request.form.get("created_time")
        # process new trip

        # get image, and image_path
        image = request.files.get("image") or None

        data, code = self.trip_service.process_new_trip(
            user_id=user_id,
            trip_name=trip_name,
            created_time=created_time,
            image=image,
        )
        return jsonify(data), code

    def end_trip(self):
        """handle end trip

        Returns:
            json: return to client
        """
        user_data_from_jwt, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401
        user_data = request.json
        ##decode jwt to get userdatas

        user_id = user_data_from_jwt.get("user_id")
        trip_id = user_data.get("trip_id")
        ended_time = user_data.get("ended_time")
        data, code = self.trip_service.end_a_trip(
            trip_id=trip_id, user_id=user_id, ended_time=ended_time
        )
        return jsonify(data), code

    def request_current_trip_id(self):
        user_data, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401
        user_id = user_data["user_id"]
        current_trip_id, code = self.trip_service.get_current_trip_id(user_id=user_id)
        return jsonify(current_trip_id), code

    def request_trip_data(self):
        """use for app api
            return tripd data
        Returns:
            _type_: _description_
        """
        # verify jwt
        user_data, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401
        user_id = user_data.get("user_id")

        client_etag = request.headers.get("If-None-Match")
        trip_id = request.json.get("trip_id")

        data, code = self.trip_service.get_trip_data(
            user_id=user_id, trip_id=trip_id, client_etag=client_etag
        )
        return jsonify(data), code

    def request_trip_data_by_shared_links(self, token):
        # get etag from browser cache to check if data has changed
        client_etag = request.headers.get("If-None-Match")

        # extract token from request body

        # validate token exists and is correct sha256 length (64 chars)
        if not token or len(token) != 64:
            return jsonify({"code": "invalid_token", "message": "Invalid token"}), 404

        trip_data, etag = self.trip_service.get_trip_data_from_token(
            client_etag=client_etag, token=token
        )
        # data unchanged — tell browser to use its cache
        if not trip_data and etag is not None:
            return jsonify({"etag": etag}), 304

        if not trip_data and not etag:
            return jsonify({"message": "failed"}), 500
        # new data — return with etag so browser can cache it
        response = jsonify({"trip_data": trip_data})
        response.headers["ETag"] = etag
        return response, 200

    def request_all_trips_data(self):
        # print(request)
        user_data, error = self._get_authenticated_user()
        # return if jwt in valid or expried

        if error:
            return jsonify(error), 401
        client_etag = request.headers.get("If-None-Match")
        user_id = user_data.get("user_id")

        all_trips_data, code = self.trip_service.get_all_trip_data(
            user_id=user_id, client_etag=client_etag, want_images=True
        )

        return jsonify(all_trips_data), code

    def request_all_trips_metadata(self):
        user_data, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401

    def change_trip_data(self):
        user_data, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401
        user_id = user_data["user_id"]

        trip_id = request.form.get("trip_id") or None
        trip_name = request.form.get("trip_name") or None
        modified_time = request.form.get("modified_time") or None
        image = request.files.get("image")
        data, code = self.trip_service.change_trip_data(
            new_trip_name=trip_name,
            trip_id=trip_id,
            user_id=user_id,
            modified_time=modified_time,
            image=image,
        )

        return jsonify(data), code

    def request_remove_trip(self):
        user_data_from_jwt, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401
        user_data = request.json
        user_id = user_data_from_jwt["user_id"]
        trip_id = user_data.get("trip_id")
        deleted_time = user_data.get("deleted_time")

        data, code = self.trip_service.remove_trip(
            user_id=user_id, trip_id=trip_id, deleted_time=deleted_time
        )
        return jsonify(data), code
