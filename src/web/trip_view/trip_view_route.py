import hashlib
import json
import os
import secrets
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from flask import Blueprint, jsonify, render_template, request

from src.base.route_base import RouteBase
from src.database.database_keys import DATABASEKEYS
from src.database.s3.s3_service import S3Sevice
from src.database.trip_db_service import TripDatabaseService
from src.database.view_trip_db_service import ViewTripDatabaseService
from src.error_handler.error_handler import ErrorHandler
from src.server_config.config import Config
from src.server_config.service.Etag.etag_services import TripShareLinksEtag
from src.server_config.service.smart_cast import smart_cast
from src.trip_contents.trip_contents_service import TripContentsService
from src.utils.cache.cache import Cache
from src.utils.route_exception import route_exception

load_dotenv(".env")
MAPTOKEN = os.getenv("MAPBOX_PUBLIC_KEY")
BASE_URL = os.getenv("BASE_URL")


class TripViewRoute(RouteBase):
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
        self.bp = Blueprint("trip-view", __name__)
        self._register_routes()
        self.TripDataBaseService = TripDatabaseService()
        self.Config = Config()
        self.ViewTripDatabaseService = ViewTripDatabaseService()
        self.S3Service = S3Sevice()
        self.TripShareLinksEtag = TripShareLinksEtag()
        self.CacheService = Cache()
        self.TripContentsService = TripContentsService()
        self._init = True

    def _register_routes(self):
        self.bp.route("/<token>", methods=["GET"])(self.request_trip_view)
        self.bp.route("/generate-trip-view-link", methods=["POST"])(
            self.generate_trip_view_link
        )
        self.bp.route("/<token>/contents", methods=["GET"])(
            self.request_trip_contents_by_token
        )

    @route_exception(
        service="Trip View Route",
        endpoint="generate_trip_view_link",
        unit="minute",
        unit_value=15,
        max_requests=75,
    )
    def generate_trip_view_link(self):
        """generate url using trip view

        Returns:
            _type_: _description_
        """
        user_data_jwt, error = self._get_authenticated_user()
        if error:
            return jsonify(error), 401
        user_data = request.json
        user_id = user_data_jwt["user_id"]
        trip_id = user_data["trip_id"]
        expired_days = user_data["expired_days"]
        if not smart_cast(trip_id) or not smart_cast(expired_days):
            return jsonify(
                {
                    "code": "invalid_type_input",
                    "message": "invalid type of input make sure it is number",
                }
            ), 401
        if not self.TripDataBaseService.trip_owner_validation(
            user_id=user_id, trip_id=trip_id
        ):
            return jsonify(
                {
                    "code": "permistion_denied",
                    "message": "Your account doesnt own or have permission to do this acction!",
                }
            ), 401
        token = self._handle_generate_trips_view_link(
            user_id=user_id, trip_id=trip_id, expired_days={"days": expired_days}
        )

        if not token:
            return jsonify(
                {"code": "failed", "message": "Failed to generate view url"}
            ), 500

        full_url = f"{BASE_URL}/trip-view/{token}"
        return jsonify(
            {
                "code": "successfully",
                "message": "Successfully create url",
                "url": full_url,
            }
        ), 200

    def _handle_generate_trips_view_link(
        self, user_id: int, trip_id: int, expired_days: object
    ) -> str:
        ex_date = datetime.now(timezone.utc) + timedelta(days=30)

        current_date = datetime.now(timezone.utc)
        random_part = secrets.token_urlsafe(16)
        raw = f"{trip_id}:{ex_date}:{random_part}"
        token = hashlib.sha256(raw.encode()).hexdigest()
        con, cur = self.TripDataBaseService.connect_db()
        cur.execute(
            f"""INSERT INTO {DATABASEKEYS.TABLES.TRIP_SHARED_LINKS} (
            {DATABASEKEYS.TRIP_SHARED_LINKS.TOKEN},
            {DATABASEKEYS.TRIP_SHARED_LINKS.USER_ID},
            {DATABASEKEYS.TRIP_SHARED_LINKS.TRIP_ID},
            {DATABASEKEYS.TRIP_SHARED_LINKS.CREATED_TIME},
            {DATABASEKEYS.TRIP_SHARED_LINKS.EXPIRED_TIME}
            ) VALUES (%s,%s,%s,%s,%s)""",
            (token, user_id, trip_id, current_date, ex_date),
        )
        con.commit()
        self.TripDataBaseService.close_db(conn=con)
        return token if cur.rowcount >= 1 else None

    @route_exception(
        service="Trip View Route",
        endpoint="request_trip_view",
        unit="minute",
        unit_value=15,
        max_requests=300,
    )
    def request_trip_view(self, token: str) -> tuple:
        try:
            print(token)

            assert token, "missing token"
            # -----------------------get from cache------------------
            cache_key = self.TripShareLinksEtag.generate_etag_key(token=token)
            cache_data = self.CacheService.get(key=cache_key)
            if cache_data:
                cache_data = json.loads(cache_data)
                return render_template(
                    "trip_view.html",
                    MAPTOKEN=MAPTOKEN,
                    BASE_URL=BASE_URL,
                    TRIP_DATA=cache_data,
                )
            # -----------------------get from database------------------

            trip_data = (
                self.ViewTripDatabaseService.get_all_trip_data_from_trip_view_token(
                    token=token
                )
            )
            if not trip_data:
                return render_template("404.html"), 404

            # ---------------------check for visibility------------------
            if trip_data["visibility"] != "public":
                return jsonify(
                    {
                        "code": "permission denied",
                        "message": f"you dont have permission to view this trip, this trip is set as {trip_data['visibility']}",
                    }
                ), 403

            # --------------check for expiration--------------
            # check if the token still valid
            if datetime.now(timezone.utc) > trip_data["expired_time"]:
                return jsonify({"code": "url_expired", "message": "Url expired!"}), 403
                # check if visibility allow

            # --------------generate presign url for image--------------
            if trip_data["image"]:
                trip_data["image"] = self.S3Service.generate_temp_uri(
                    trip_data["image"]
                )

            # --------------set to cache-------------------------
            self.CacheService.set(
                key=cache_key, data=json.dumps(trip_data, default=str), time=3600
            )

            return render_template(
                "trip_view.html",
                MAPTOKEN=MAPTOKEN,
                BASE_URL=BASE_URL,
                TRIP_DATA=trip_data,
            )
        except AssertionError as e:
            return render_template("404.html"), 400
        except Exception as e:
            print(e)
            return jsonify(
                {
                    "code": "failed",
                    "message": f"Server failed: {str(e)}",
                }
            ), 500
        # if pass we get ready to return template

    @route_exception(
        service="Trip View Route",
        endpoint="request_trip_contents_by_token",
        unit="minute",
        unit_value=15,
        max_requests=300,
    )
    def request_trip_contents_by_token(self, token: str):
        try:
            assert token, "token empty"
            # -----------------------get data straight from cache----------
            cache_key = self.TripShareLinksEtag.generate_etag_key(token=token)
            trip_data = self.CacheService.get(key=cache_key)

            if not trip_data:
                return jsonify({"code": "not_found", "message": "Trip Not Found"}), 403
            trip_data = json.loads(trip_data)
            trip_id = trip_data.get("trip_id")
            user_id = trip_data.get("user_id")
            trip_contents, code = (
                self.TripContentsService.get_all_content_card_from_trip_id(
                    trip_id=trip_id, user_id=user_id
                )
            )

            return jsonify(trip_contents), code
            # -----------------------get trip contents----------------

        except AssertionError as e:
            return jsonify({"code": "missing_input", "message": "Missing token"}), 403
