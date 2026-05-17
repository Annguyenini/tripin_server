import os

import dotenv
from flask import request

from src.token.tokenservice import TokenService

dotenv.load_dotenv()


class RouteBase:
    _instance = None
    _init = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init:
            return
        self.tokenService = TokenService()
        self._init = True

    def _get_request_ip_address(self):
        if os.getenv("DEBUG"):
            return request.remote_addr
        else:
            return request.headers.get("X-Forwarded-For", request.remote_addr)

    def _get_authenticated_user(self) -> tuple[dict | None, dict | None]:
        # verify jwt
        Ptoken = request.headers.get("Authorization")
        token = Ptoken.replace("Bearer ", "")
        valid_token, message, code = self.tokenService.jwt_verify(token)
        # return if jwt in valid or expried
        if not valid_token:
            return None, {"message": message, "code": code}

        user_data = self.tokenService.decode_jwt(
            token=token, fields=["user_id", "role"]
        )
        return dict(user_data), None

    def _user_jwt_validation_policy(self) -> tuple[dict | None]:
        try:
            Ptoken = request.headers.get("Authorization")
            token = Ptoken.replace("Bearer ", "")
            valid_token, message, code = self.tokenService.jwt_verify(token)
            # return if jwt in valid or expried
            if not valid_token:
                raise PermissionError(code)

            user_data = self.tokenService.decode_jwt(
                token=token, fields=["user_id", "role"]
            )
            return dict(user_data)
        except PermissionError as p:
            raise
        except Exception as e:
            raise PermissionError("failed to validate jwt")
