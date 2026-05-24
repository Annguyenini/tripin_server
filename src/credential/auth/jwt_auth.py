from src.credential.credential_base import CredentialBase


class JWTAuthenticationService(CredentialBase):
    _instance = None
    _init = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._init:
            return
        super().__init__()
        self._init = True

    def login_via_token(self, token: str) -> tuple[dict, int]:
        try:
            status, message, code = self.TokenService.jwt_verify(token)

            if not status:
                return {
                    "message": message,
                    "code": code,
                    "user_data": None,
                }, 401

            # get userdata from token
            userdata_from_jwt = self.TokenService.decode_jwt(
                token, fields=["user_id", "role"]
            )

            user_id = userdata_from_jwt["user_id"]
            role = userdata_from_jwt["role"]

            user_data = {"user_id": user_id, "role": role}

            return {
                "message": message,
                "user_data": user_data,
                "code": "successfully",
            }, 200
        except AssertionError as e:
            return {"code": "missing_inputs", "message": str(e)}
        except Exception as e:
            self._credential_logger().error("failed to login with access_token", {e})
            return {"code": "failed", "message": "Failed to complete request!"}, 500

    def request_new_access_token(self, refresh_token: str) -> tuple[dict, int]:
        try:
            assert refresh_token, "token is empty"
            # check if token expired
            status, message, code = self.TokenService.jwt_verify(token=refresh_token)
            if not status:
                return (
                    {"code": "failed", "message": "Could not finish the request!"}
                ), 401

            # check refresh token in database
            refresh_token_verify = self.TokenDatabaseService.verify_refresh_token(
                refresh_token=refresh_token
            )
            if not refresh_token_verify:
                return {"code": "token_invalid"}, 401

            # get userdata from token

            userdata_from_jwt = self.TokenService.decode_jwt(
                token=refresh_token, fields=["user_id", "role"]
            )

            user_id = userdata_from_jwt["user_id"]
            role = userdata_from_jwt["role"]
            # generate new access token

            new_access_token = self.TokenService.generate_jwt(
                fields={"user_id": user_id, "role": role}
            )
            return ({"message": "Successfully", "token": new_access_token}), 200
        except AssertionError as e:
            return (
                {
                    "code": "missing_inputs",
                    "message": str(e),
                }
            ), 404
        except Exception as e:
            self._credential_logger().error("failed to request new access_token", {e})
            return (
                {
                    "code": "failed",
                    "message": "Failed",
                }
            ), 404
