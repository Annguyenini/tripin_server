# import email
import os
from collections import UserDict
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import requests
from flask.json import jsonify
from google.auth.transport import requests
from google.oauth2 import id_token
from werkzeug.security import check_password_hash, generate_password_hash

from src.audit.userdata_audit import UserdataAudit
from src.database.database import Database
from src.database.database_keys import DATABASEKEYS
from src.database.s3.s3_dirs import AVATAR_DIR, TRIP_DIR
from src.database.s3.s3_service import S3Sevice
from src.database.userdata_db_service import UserDataDataBaseService
from src.error_code.error_code import INPUT_ERROR
from src.error_handler.error_handler import ErrorHandler
from src.logger.logging import get_logger
from src.mail.mail_service import MailService
from src.server_config.service.cache import Cache
from src.server_config.service.input_validation import InputValidation
from src.token.tokenservice import TokenService
from src.trip_service.trip_service import TripService
from src.user.user_service import UserService

# userdata user_id|email|user_name|displayname|password
# token keyid| userid| username|token|issue name | exp name | revok
#
#
TOKENSTATUS = SimpleNamespace(
    PENDING="pending", VERIFIED="verified", COMPLETED="completed"
)
TOKENACTION = SimpleNamespace(
    RESET_PASSWORD="reset_password",
    SIGNUP_VIA_PROVIDER="signup_via_provider",
)


class Auth:
    _instance = None
    _initialize = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialize:
            self.db = Database()
            self.tokenService = TokenService()
            self.mail_service = MailService()
            self.tripService = TripService()
            self.userService = UserService()
            self.inputValidationService = InputValidation()
            self.errorHandler = ErrorHandler()
            self.UserDatabaseService = UserDataDataBaseService()
            self.UserdataAudit = UserdataAudit()
            self.user_queue = {}
            self.logger = get_logger(__name__)

            self._initialize = True

    # login function
    def login(self, password: str, username: str | None, email: str | None):
        """Login fuction use for process call jwt generate, verify credential

        Returns:
            bool : status
            tuple: user_id|display_name|user_name|refresh_token|access_token|role
            tuple:
        """
        # verify user input
        try:
            if username:
                if not self.inputValidationService.username_validation(
                    username=username
                ):
                    raise ValueError(INPUT_ERROR.USERNAME)
            elif email:
                if not self.inputValidationService.email_validation(email=email):
                    raise ValueError(INPUT_ERROR.EMAIL)
            else:
                raise ValueError("Empty")

            if not self.inputValidationService.password_validation(password=password):
                raise ValueError(INPUT_ERROR.PASSWORD)
            ##find username in database
            userdata_row = None
            if username:
                userdata_row = (
                    self.UserDatabaseService.get_user_data_by_email_or_username(
                        value=username
                    )
                )
            elif email:
                userdata_row = (
                    self.UserDatabaseService.get_user_data_by_email_or_username(
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
                    400,
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
            self.errorHandler.logger("auth").error("Failed at request login", {e})
            return None, None

    # signup function
    def signup(self, email: str, display_name: str, username: str, password: str):
        try:
            if not self.inputValidationService.email_validation(email=email):
                raise ValueError(INPUT_ERROR.EMAIL)
            if not self.inputValidationService.username_validation(username=username):
                raise ValueError(INPUT_ERROR.USERNAME)
            if not self.inputValidationService.displayname_validation(
                display_name=display_name
            ):
                raise ValueError(INPUT_ERROR.DISPLAY_NAME)
            if not self.inputValidationService.password_validation(password=password):
                raise ValueError(INPUT_ERROR.PASSWORD)

            ## if the Email already exists in database, return
            if self.UserDatabaseService.get_user_data_by_email(email=email):
                return {
                    "code": "email_exists",
                    "message": "Email already link to an account!",
                }, 400

            ## if the username already exists in database, return
            if self.UserDatabaseService.get_user_data_by_username(user_name=username):
                return {
                    "code": "username_exists",
                    "message": "Username already exists in the database!",
                }, 400

            ## process to verify email
            respond = self.mail_service.send_confirmation_code(email)

            ##hash password, prepare to insert to database
            hashed_passwords = generate_password_hash(password)

            if respond:
                data = {
                    "email": email,
                    "display_name": display_name,
                    "username": username,
                    "password": hashed_passwords,
                }
                self.user_queue[email] = data
                return True, "Successfully"
            else:
                return False, "Error at signup"

        except Exception as e:
            print(e)
            return False, "Error at signup"

    def login_via_token(self, token: str) -> tuple[dict, int]:

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

    def process_new_user(self, email: str):
        # assert(type(email) is not str,"Email should be string")
        data = self.user_queue.get(email)
        if data is None:
            return {"error": "Session expired"}, 400
        display_name = data.get("display_name")
        username = data.get("username")
        password = data.get("password")
        res = self.UserDatabaseService.insert_new_userdata(
            email=email, username=username, display_name=display_name, password=password
        )
        if res < 0:
            return False
        return True

    def confirm_code(self, email: str, code: int):
        # input validation
        if not self.inputValidationService.email_validation(email=email):
            return False, INPUT_ERROR.EMAIL
        if not self.inputValidationService.verify_code_valiation(code=code):
            return False, INPUT_ERROR.VERIFY_CODE
        # calling varify method
        respond = self.mail_service.verify_code(recipients=email, code=code)

        if not respond:
            return False

        process_new_user = self.process_new_user(email=email)
        if not process_new_user:
            return False
        return True

    def request_reset_password(
        self, email: str, ip_address: str
    ) -> tuple[bool, dict | None, int]:
        try:
            # verify email if it in the database
            userdata = self.UserDatabaseService.get_user_data_by_email(email=email)
            if not userdata:
                return False, {"code": "email_not_exists"}, 404
            email = userdata["email"]
            user_id = userdata["id"]
            # generate token with status pending
            token_session = self.tokenService.generate_jwt(
                fields={
                    "email": email,
                    "user_id": user_id,
                    "action": "reset_password",
                    "status": "pending",
                    "ip_address": ip_address,
                },
                exp_time={"minutes": 5},
            )
            # send code, return token for next step
            send_code = self.mail_service.send_confirmation_code(recipients=email)
            if not send_code:
                return False, {"code": "server_failed", "token": None}, 500
            return True, {"code": "successfully", "token": token_session}, 200
        except Exception as e:
            self.errorHandler.logger("Auth").error(
                "Failed at request reset password", {e}
            )
            return False, {"code": "server_failed", "token": None}, 500

    def request_reset_password_verify(
        self, code: int, token: str
    ) -> tuple[bool, dict, int]:
        # guard
        if not code or not token:
            return False, {"code": "invalid_code_or_token"}, 404
        try:
            # get data from token
            user_data = self.tokenService.decode_jwt(
                token=token, fields=["user_id", "email", "status", "action"]
            )
            # guard for token, make sure right token been use
            print(user_data)
            status = user_data["status"]
            action = user_data["action"]
            if action != "reset_password" or status != "pending":
                return False, {"code": "invalid_token"}, 404
            email = user_data["email"]
            user_id = user_data["user_id"]

            # verify code t0 match
            verify = self.confirm_code(email=email, code=code)

            if not verify:
                return False, {"code": "code_not_match"}, 404
            # after verified, generate token that have status 'verified',
            # return for next step
            token_session = self.tokenService.generate_jwt(
                fields={
                    "email": email,
                    "user_id": user_id,
                    "action": "reset_password",
                    "status": "verified",
                    "ip_address": user_data["ip_address"],
                },
                exp_time={"minutes": 5},
            )
            return True, {"token": token_session, "code": "successfully"}, 200
        except Exception as e:
            self.errorHandler.logger("Auth").error(
                "Failed at reset password verify", {e}
            )
            return False, {}, 500
        pass

    def reset_password_handler(self, token: str, new_password: str):
        try:
            # guard
            if not token:
                return False, {"code": "invalid_token"}, 404
            if not self.inputValidationService.password_validation(
                password=new_password
            ):
                return False, {"code": INPUT_ERROR.PASSWORD}, 404
            user_data = self.tokenService.decode_jwt(
                token=token, fields=["user_id", "email", "status", "action"]
            )
            action = user_data["action"]
            status = user_data["status"]
            ip_address = user_data["ip_address"]
            # guard for token
            if action != "reset_password" or status != "verified":
                return False, {"code": "invalid_token"}, 404
            user_id = user_data["user_id"]
            # old data , old password we could enforce new password != old password in the future
            old_userdata = self.UserDatabaseService.get_user_data_by_id(user_id=user_id)
            old_password = old_userdata["password"]

            new_hased_password = generate_password_hash(password=new_password)
            update = self.UserDatabaseService.update_user_password(
                user_id=user_id, new_hashed_password=new_hased_password
            )
            # audit
            self.UserdataAudit.update_user_audit(
                user_id=user_id,
                modified_time=str(datetime.now()),
                action="reset_password",
                ip_address=ip_address,
                old_value=old_password,
                new_value=new_hased_password,
            )
            if not update:
                return False, {"code": "server_failed"}, 500
            return True, {"code": "successfully"}, 200
            pass
        except Exception as e:
            self.errorHandler.logger("Auth").error("Failed at reset password", {e})
            return False, None, 500
            pass

    def _email_verify(self, email: str):
        if not self.inputValidationService.email_validation(email=email):
            return False, INPUT_ERROR.EMAIL
        exists = self.UserDatabaseService.get_user_data_by_email(email=email)
        if exists:
            return False, "email_exists"
        return True, "successfully"

    def _provider_verification_google(self, token: str):
        WEB_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
        IOS_CLIENT_ID = os.environ.get("IOS_CLIENT_ID")
        CLIENT_ID = [WEB_CLIENT_ID, IOS_CLIENT_ID]
        id_info = None
        for client in CLIENT_ID:
            try:
                id_info = id_token.verify_oauth2_token(
                    token, requests.Request(), client
                )
                break
            except Exception as e:
                continue
        if not id_info:
            return None
        email = id_info["email"]
        name = id_info["name"]
        provider_id = id_info["sub"]

        return {"email": email, "name": name, "provider_id": provider_id}

    def _jwt_cycle_handler(self, user_id: int, role: str):
        # old token got revoked
        self.tokenService.revoke_refresh_token(user_id=user_id)

        # new tokens generated
        refresh_token = self.tokenService.generate_jwt(
            fields={"user_id": user_id, "role": role}, exp_time={"days": 30}
        )
        access_token = self.tokenService.generate_jwt(
            fields={"user_id": user_id, "role": role}, exp_time={"minutes": 15}
        )
        token_data = {"access_token": access_token, "refresh_token": refresh_token}

        ##inserted token into database
        self.db.insert_token_into_db(
            user_id=user_id,
            token=refresh_token,
            issued_at=datetime.now(timezone.utc),
            expired_at=datetime.now(timezone.utc) + timedelta(days=30),
        )
        return token_data
