from werkzeug.security import check_password_hash, generate_password_hash

from src.credential.credential_base import CredentialBase
from src.server_config.service.input_validation import CredentialInputValidation
from src.utils.route_exception import route_exception


class LoginService(CredentialBase):
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

        self.CredentialInputValidation = CredentialInputValidation()

        self._init = True

    def login(self, password: str, username: str | None, email: str | None):
        """Login fuction use for process call jwt generate, verify credential

        Returns:
            bool : status
            tuple: user_id|display_name|user_name|refresh_token|access_token|role
            tuple:
        """
        # verify user input
        try:
            self.CredentialInputValidation.login_input_validation(
                username=username, password=password, email=email
            )
            ##find username in database
            userdata_row = None
            if username:
                userdata_row = (
                    self.UserDataBaseService.get_user_data_by_email_or_username(
                        value=username
                    )
                )
            elif email:
                userdata_row = (
                    self.UserDataBaseService.get_user_data_by_email_or_username(
                        value=email
                    )
                )
            ##return false if username not exist
            if userdata_row is None:
                return (
                    {
                        "message": "Wrong username or email",
                        "user_data": None,
                    },
                    401,
                )

            userid = userdata_row["id"]
            # checker
            role = userdata_row["role"]

            # if user is found and password is correct
            if not check_password_hash(userdata_row["password"], password):  # password
                return (
                    {
                        "message": "Wrong password",
                        "user_data": None,
                        "trip_data": None,
                        "tokens": None,
                        "all_trip_data": None,
                    },
                    403,
                )

            # user data
            user_data = {"user_id": userid, "role": role}

            token_data = self._jwt_cycle_handler(user_id=userid, role=role)

            return (
                {
                    "message": "Successfully",
                    "user_data": user_data,
                    "tokens": token_data,
                },
                200,
            )
        except ValueError as e:
            return {"code": "input_validation_failed", "message": str(e)}, 400
        except Exception as e:
            self._credential_logger().error("Failed at request login", {e})
            return {"code": "failed"}, 500
