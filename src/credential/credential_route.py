##before pass into service fucntions, this help filter info and verify jwt token for unnesscary function call
##rate limit are set as 5 requests total per min

from ipaddress import ip_address

from flask import Blueprint, jsonify, request

from src.base.route_base import RouteBase
from src.credential.credential import Auth
from src.server_config.service.cache import Cache
from src.token.tokenservice import TokenService


class AuthServer(RouteBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.bp = Blueprint("auth", __name__)
        self.auth = Auth()
        self.token_service = TokenService()
        self.rate_limiter_service = Cache()
        self._register_routes()

    def _register_routes(self):
        """Auth Route
        Each have rate limiter of 5 per minute in total
        """
        # pass the bound method
        # #rate limiter
        # @self.bp.before_request
        # def rate_limit():
        #     user_ip = request.remote_addr
        #     count = self.rate_limiter_service.incr(user_ip)
        #     if count ==1:
        #         self.rate_limiter_service.exp(user_ip,60)
        #     elif count>5:
        #         return jsonify({"message":"Too many request!"}),429

        self.bp.route("/login-via-token", methods=["POST"])(self.login_via_token)
        self.bp.route("/login", methods=["POST"])(self.login)
        self.bp.route("/signup", methods=["POST"])(self.signup)
        self.bp.route("/request-access-token", methods=["POST"])(
            self.request_new_access_token
        )
        self.bp.route("/verify-code", methods=["POST"])(self.verify_code)
        self.bp.route("/provider/<provider>", methods=["POST"])(self.provider_verify)
        self.bp.route("/provider/complete-signup", methods=["POST"])(
            self.singup_provider
        )
        self.bp.route("/reset-password", methods=["POST"])(self.request_reset_password)
        self.bp.route("/reset-password/verify", methods=["POST"])(
            self.request_reset_password_verify
        )
        self.bp.route("/reset-password/reset", methods=["POST"])(
            self.request_reset_password_complete
        )

    def verify_code(self):
        """User verify code, get user data and pass to a function to check the code"""
        data = request.json
        recipients = data.get("email")
        email = recipients.lower()
        str_code = data.get("code")
        code = int(str_code)
        respond = self.auth.confirm_code(email, code)

        if not respond:
            return jsonify({"status": "Failed"}), 404
        process_new_user = self.auth.process_new_user(email=email)
        if not process_new_user:
            return jsonify({"status": "Failed"}), 500
        return jsonify({"status": "Successfully"}), 200

    def login_via_token(self):
        """
        Docstring for login_via_token

        :param self: get token from header verify token
        """
        ptoken = request.headers.get("Authorization")
        token = ptoken.replace("Bearer ", "")

        data = self.auth.login_via_token(token=token)

        status = data["status"]
        message = data["message"]
        code = data["code"]
        user_data = data["user_data"]

        if not status:
            return jsonify({"message": message, "user_data": None, "code": code}), 401

        return jsonify({"message": message, "user_data": user_data}), 200

    def login(self):
        data = request.json
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        status, login_process = self.auth.login(
            username=username, password=password, email=email
        )
        message = login_process["message"]
        if not status:
            return jsonify({"message": message}), 401
        user_data = login_process["user_data"]
        tokens = login_process["tokens"]

        return jsonify(
            {"message": message, "tokens": tokens, "user_data": user_data}
        ), 200

    def signup(self):
        data = request.json
        email = data.get("email")
        display_name = data.get("displayName")
        username = data.get("username")
        password = data.get("password")
        lower_case_email = email.lower()
        status, message = self.auth.signup(
            email=lower_case_email,
            display_name=display_name,
            username=username,
            password=password,
        )
        if not status:
            return jsonify({"message": message}), 401
        return jsonify({"message": message}), 200

    def request_new_access_token(self):
        data = request.headers.get("Authorization")
        if not data:
            return jsonify(
                {
                    "code": "invalid_token",
                    "message": "Failed",
                }
            ), 404
        token = data.replace("Bearer ", "")
        status, new_token = self.token_service.request_new_access_token(token)
        if not status:
            return jsonify({"message": "Could not finish the request!"}), 401
        return jsonify({"message": "Successfully", "token": new_token}), 200

    def request_reset_password(self):
        user_data = request.json
        ip_address = request.remote_addr
        email = user_data.get("email")
        res, data, code = self.auth.request_reset_password(
            email=email, ip_address=ip_address
        )
        return jsonify(data), code

    def request_reset_password_verify(self):
        user_data = request.json
        token = user_data.get("token")
        verify_code = user_data.get("code")
        res, data, code = self.auth.request_reset_password_verify(
            code=verify_code, token=token
        )
        return jsonify(data), code

    def request_reset_password_complete(self):
        user_data = request.json
        token = user_data.get("token")
        new_password = user_data.get("new_password")

        res, data, code = self.auth.reset_password_handler(
            new_password=new_password, token=token
        )
        return jsonify(data), code

    def provider_verify(self, provider):
        user_data = request.json
        id_token = user_data["id_token"]
        verify, data = self.auth.provider_verify(provider=provider, token=id_token)
        if not verify:
            return jsonify(data), 400
        if data.get("code") == "pending":
            return jsonify(data), 202
        return jsonify(data), 200

    def singup_provider(self):
        try:
            user_data = request.json
            token = user_data["pending_token"]
            username = user_data["username"]
            display_name = user_data["display_name"]
            password = user_data["password"]
            status, code = self.auth.provider_signup_complete(
                token=token,
                username=username,
                display_name=display_name,
                password=password,
            )
            if not status:
                return jsonify(code), 500
            return jsonify(code), 200
        except Exception as e:
            print(e)
            return ("failed"), 500

    # def signin_provider_verify(self):
    #     user_data = request.json
    #     provider_id = user_data['provider_id']
    #     pass
