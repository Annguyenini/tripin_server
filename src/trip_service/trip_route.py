import json
from crypt import methods

from flask import Blueprint, jsonify, request

from src.base.route_base import RouteBase
from src.database.s3.s3_dirs import TRIP_DIR
from src.database.s3.s3_service import S3Sevice
from src.database.trip_db_service import TripDatabaseService
from src.token.tokenservice import TokenService
from src.trip_service.trip_service import TripService
from src.utils.cache.cache import Cache
from src.utils.handle_exception import handle_exception


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
        self.trip_s3 = S3Sevice()
        self.cache_service = Cache()
        self.trip_database_service = TripDatabaseService()
        self._init = True
        self._register_route()

    def _register_route(self):
        self.bp.route("/new-trip", methods=["POST"])(self.request_new_trip)
        self.bp.route("/trip-cover-upload-verification", methods=["POST"])(
            self.trip_cover_verification
        )
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
        try:
            user_data_from_jwt, error = self._get_authenticated_user()
            if error:
                return jsonify(error), 401
            ##decode jwt to get userdatas
            user_id = user_data_from_jwt.get("user_id")
            body = request.get_json(silent=True)
            if not body:
                return jsonify(
                    {"code": "invalid_body", "message": "JSON body required"}
                ), 400

            trip_name = body.get("trip_name")
            created_time = body.get("created_time")
            image = bool(body.get("image"))

            if not trip_name or not created_time:
                return jsonify(
                    {
                        "code": "missing_inputs",
                        "message": "trip_name and created_time are required",
                    }
                ), 400

            data, code = self.trip_service.process_new_trip(
                user_id=user_id,
                trip_name=trip_name,
                created_time=created_time,
                image=image,
            )

            return jsonify(data), code
        except ValueError as e:
            pass
        except Exception as e:
            return {"code": "server_failed"}, 500

    def trip_cover_verification(self):
        """take in user data to process new trip

        Returns:
            status: html status, message
        """
        user_data_from_jwt, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401
        ##decode jwt to get userdatas

        user_id = user_data_from_jwt.get("user_id")
        userdata = request.get_json(silent=True)
        pending_token = userdata.get("pending_token")
        modified_time = userdata.get("modified_time")
        if not pending_token or not modified_time:
            return {"code": "missing_inputs", "message": "Missing Inputs!"}, 400
        data, code = self.trip_service.trip_cover_verification(
            pending_token=pending_token, modified_time=modified_time, user_id=user_id
        )
        print(data, code)
        return jsonify(data), code

    def end_trip(self):
        """handle end trip

        Returns:
            json: return to client
        """
        user_data_from_jwt, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401

        user_id = user_data_from_jwt.get("user_id")
        body = request.get_json(silent=True)
        ##decode jwt to get userdatas

        trip_id = body.get("trip_id")
        ended_time = body.get("ended_time")
        if not trip_id or not ended_time:
            return {"code": "missing_inputs", "message": "Missing inputs"}
        data, code = self.trip_service.request_end_trip(
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

    @handle_exception("Trip Route", "request trip data")
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
        if not trip_id:
            return {"code": "missing inputs", "message": "Missing Inputs"}, 400
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
            user_id=user_id, client_etag=client_etag
        )

        return jsonify(all_trips_data), code

    def request_all_trips_metadata(self):
        user_data, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401

    def change_trip_data(self):
        user_data_from_jwt, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401
        user_id = user_data_from_jwt["user_id"]

        user_data = request.json
        trip_id = user_data.get("trip_id")
        new_trip_name = user_data.get("trip_name", None)
        modified_time = user_data.get("modified_time")
        image = bool(user_data.get("image"))
        data, code = self.trip_service.change_trip_data(
            new_trip_name=new_trip_name,
            trip_id=trip_id,
            user_id=user_id,
            modified_time=modified_time,
            image=image,
        )

        return jsonify(data), code

    @handle_exception("Trip Service Route", "request remove trip")
    def request_remove_trip(self):
        user_data_from_jwt, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401
        body = request.get_json(silent=True)
        user_id = user_data_from_jwt["user_id"]
        trip_id = body.get("trip_id")
        deleted_time = body.get("deleted_time")
        if not trip_id or not deleted_time:
            return {
                "code": "missing_inputs",
                "message": "missing trip_id or deleted_time",
            }
        data, code = self.trip_service.remove_trip(
            user_id=user_id, trip_id=trip_id, deleted_time=deleted_time
        )
        return jsonify(data), code
