##before pass into service fucntions, this help filter info and verify jwt token for unnesscary function call
##rate limit are set as 5 requests total per min


import re

from flask import Blueprint, jsonify, request

from middleware.rate_limiter import ClientProperties, RateLimiter, RateLimiterProperties
from src.base.route_base import RouteBase
from src.credential.auth.jwt_auth import JWTAuthenticationService
from src.credential.auth.login_service import LoginService
from src.credential.auth.reset_password import ResetPasswordService
from src.credential.auth.signup_service import SignupService
from src.credential.provider.provider_auth import ProviderAuth
from src.token.tokenservice import TokenService
from src.utils.cache.cache import Cache
from src.utils.route_exception import route_exception


class AuthServer(RouteBase):
    _instance = None
    _init = False
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init:return
        super().__init__()
        self.bp = Blueprint("auth", __name__)
        self.token_service = TokenService()
        self.rate_limiter_service = Cache()
        self.LoginService = LoginService()
        self.JwtAuthenticationService = JWTAuthenticationService()
        self.ResetPasswordService = ResetPasswordService()
        self.SignupService = SignupService()
        self.ProviderService = ProviderAuth()
        self._register_routes()
        self._init = True

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

    # --------------JWT authentication---------------
    @route_exception(
        service="Auth Route",
        endpoint="login",
        unit="second",
        unit_value=60,
        max_requests=7,
    )
    def login_via_token(self):
        """
        Docstring for login_via_token

        :param self: get token from header verify token
        """
        ptoken = request.headers.get("Authorization")
        token = ptoken.replace("Bearer ", "")

        data, code = self.JwtAuthenticationService.login_via_token(token=token)
        return jsonify(data), code

    # --------------Request new access token--------
    @route_exception(
        service="Auth Route",
        endpoint="login",
        unit="minute",
        unit_value=15,
        max_requests=7,
    )
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
        respond, code = self.JwtAuthenticationService.request_new_access_token(
            refresh_token=token
        )
        return jsonify(respond), code

    # ---------------Login-----------------------------
    @route_exception(
        service="Auth Route",
        endpoint="login",
        unit="minute",
        unit_value=15,
        max_requests=5,
    )
    def login(self):
        data = request.json
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        data, code = self.LoginService.login(
            username=username, password=password, email=email
        )
        return jsonify(data), code

    @route_exception(
        service="Auth Route",
        endpoint="signup",
        unit="minute",
        unit_value=15,
        max_requests=3,
    )
    # --------------Sign up --------------------------
    def signup(self):
        data = request.json
        email = data.get("email")
        display_name = data.get("displayName")
        username = data.get("username")
        password = data.get("password")
        lower_case_email = email.lower()
        respond, code = self.SignupService.signup(
            email=lower_case_email,
            display_name=display_name,
            username=username,
            password=password,
        )
        return jsonify(respond), code

    @route_exception(
        service="Auth Route",
        endpoint="signup-verify",
        unit="minute",
        unit_value=15,
        max_requests=3,
    )
    def verify_code(self):
        """User verify code, get user data and pass to a function to check the code"""
        data = request.json
        recipients = data.get("email")
        email = recipients.lower()
        str_code = data.get("code")
        code = int(str_code)
        respond, respond_code = self.SignupService.confirm_code_and_process_new_user(
            email=email, code=code
        )

        return jsonify(respond), respond_code

    # ------reset password--------------

    @route_exception(
        service="Auth Route",
        endpoint="reset password",
        unit="minute",
        unit_value=15,
        max_requests=5,
    )
    def request_reset_password(self):
        user_data = request.json
        email = user_data.get("email")
        data, code = self.ResetPasswordService.request_reset_password(email=email)
        return jsonify(data), code

    @route_exception(
        service="Auth Route",
        endpoint="request_reset_password_verify",
        unit="minute",
        unit_value=15,
        max_requests=5,
    )
    def request_reset_password_verify(self):
        user_data = request.json
        email = user_data.get("email")
        verify_code = user_data.get("code")
        data, code = self.ResetPasswordService.request_reset_password_verify(
            code=verify_code, email=email
        )
        return jsonify(data), code

    @route_exception(
        service="Auth Route",
        endpoint="request_reset_password_complete",
        unit="minute",
        unit_value=15,
        max_requests=5,
    )
    def request_reset_password_complete(self):
        user_data = request.json
        token = user_data.get("token")
        email = user_data.get("email")
        ip_address = self._get_request_ip_address()
        new_password = user_data.get("new_password")

        data, code = self.ResetPasswordService.reset_password_handler(
            new_password=new_password, token=token, email=email, ip_address=ip_address
        )
        return jsonify(data), code

    # --------------Provider--------------------
    #
    @route_exception(
        service="Auth Route",
        endpoint="provider_verify",
        unit="minute",
        unit_value=15,
        max_requests=3,
    )
    def provider_verify(self, provider):
        user_data = request.json
        id_token = user_data["id_token"]
        data, code = self.ProviderService.provider_verify(
            provider=provider, token=id_token
        )

        return jsonify(data), code

    @route_exception(
        service="Auth Route",
        endpoint="singup_provider",
        unit="minute",
        unit_value=15,
        max_requests=3,
    )
    def singup_provider(self):
        try:
            user_data = request.json
            token = user_data["pending_token"]
            username = user_data["username"]
            display_name = user_data["display_name"]
            password = user_data["password"]
            data, code = self.ProviderService.provider_signup_complete(
                token=token,
                username=username,
                display_name=display_name,
                password=password,
            )
            print(data)
            return jsonify(data), code
        except Exception as e:
            print(e)
            return ("failed"), 500

    # def signin_provider_verify(self):
    #     user_data = request.json
    #     provider_id = user_data['provider_id']
    #     pass
