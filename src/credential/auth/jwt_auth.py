from werkzeug.security import check_password_hash, generate_password_hash

from src.database.token_db_service import TokenDatabaseService
from src.error_code.error_code import INPUT_ERROR
from src.server_config.service.input_validation import InputValidation
from src.token.tokenservice import TokenService


class LoginService:
    _instance = None
    _init = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._init:
            return
        self.inputValidationService = InputValidation()
        self.tokenService = TokenService()
        self.tokenDatabaseService = TokenDatabaseService()
        self._init = True

    def login_via_token(self, token: str):

        status, message, code = self.tokenService.jwt_verify(token)
        # print(status,message,code
        # if token invalid or expried, return
        if not status:
            return {
                "status": False,
                "message": message,
                "code": code,
                "user_data": None,
            }, 401

        # get userdata from token
        userdata_from_jwt = self.tokenService.decode_jwt(
            token, fields=["user_id", "role"]
        )

        user_id = userdata_from_jwt["user_id"]
        role = userdata_from_jwt["role"]

        user_data = {"user_id": user_id, "role": role}

        return {
            "status": True,
            "message": message,
            "user_data": user_data,
            "code": code,
        }, 200

    def request_new_access_token(self, refresh_token: str):
        try:
            assert refresh_token, "token is empty"
            # check if token expired
            status, message, code = self.tokenService.jwt_verify(token=refresh_token)
            if not status:
                return (
                    {"code": "failed", "message": "Could not finish the request!"}
                ), 401

            # check refresh token in database
            refresh_token_verify = self.tokenDatabaseService.verify_refresh_token(
                refresh_token=refresh_token
            )
            if not refresh_token_verify:
                return {"code": "token_invalid"}, 401

            # get userdata from token

            userdata_from_jwt = self.tokenService.decode_jwt(
                token=refresh_token, fields=["user_id", "role"]
            )

            user_id = userdata_from_jwt["user_id"]
            role = userdata_from_jwt["role"]
            # generate new access token

            new_access_token = self.tokenService.generate_jwt(
                fields={"user_id": user_id, "role": role}
            )
            return ({"message": "Successfully", "token": new_access_token}), 200
        except AssertionError as e:
            return (
                {
                    "code": "invalid_token",
                    "message": "Failed",
                }
            ), 404
