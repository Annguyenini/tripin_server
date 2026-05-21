import json
import secrets
from random import random

from werkzeug.security import check_password_hash, generate_password_hash

from src.credential.credential_base import CredentialBase
from src.error_code.error_code import INPUT_ERROR


class SignupService(CredentialBase):
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

    def _generate_user_process_queue_key(self, code: str) -> str:
        return f"process_new_user::{code}"

    def _generate_email_confirm_code_key(self, email: str) -> str:
        return f"email_confirmation::{email}"

    def signup(self, email: str, display_name: str, username: str, password: str):
        try:
            # ----------Input validation---------------------
            # inputs validation

            self.CredentialInputValidation.signup_input_validation(
                username=username,
                display_name=display_name,
                password=password,
                email=email,
            )
            # ---------Exists email, username check---------
            ## if the Email already exists in database, return
            if self.UserDataBaseService.get_user_data_by_email(email=email):
                return {
                    "code": "email_exists",
                    "message": "Email or username already in use",
                }, 400

            ## if the username already exists in database, return
            if self.UserDataBaseService.get_user_data_by_username(user_name=username):
                return {
                    "code": "username_exists",
                    "message": "Email or username already in use!",
                }, 400

            # ----------Process sending confirmation code----
            ## process to verify email
            random_code = secrets.randbelow(900000) + 100000

            send_code = self.CredentialEmailService.send_email_confirmation_code(
                code=random_code, recipient=email
            )
            if not send_code:
                return {
                    "code": "failed",
                    "message": "Failed to send confirmation code!",
                }, 500

            # ----------generate pending userdata---------
            # hash password, prepare to insert to database
            hashed_passwords = generate_password_hash(password)

            data = {
                "email": email,
                "display_name": display_name,
                "username": username,
                "password": hashed_passwords,
            }

            # --------check if OTP in cache------------------------
            #
            # if (
            #     self.CacheService.get(
            #         key=self._generate_email_confirm_code_key(email=email)
            #     )
            #     is None
            # ):
            #     return {"code": "pending", "message": "OTP on the way"}, 400

            # --------put into cache------------------------
            #
            self.CacheService.set(
                key=self._generate_email_confirm_code_key(email=email),
                data=random_code,
                time=300,
            )
            self.CacheService.set(
                key=self._generate_user_process_queue_key(code=random_code),
                data=json.dumps(data),
                time=300,
            )
            return {"code": "pending", "message": "Pending"}, 201

        except ValueError as e:
            return {"code": "missing_input", "message": str(e)}, 400
        except Exception as e:
            self._credential_logger().error("failed to solve signup", {e})
            return {"code": "failed"}, 500

    def confirm_code_and_process_new_user(
        self, email: str, code: str
    ) -> tuple[dict, int]:
        try:
            # ------------verify code validation----------
            # input validation
            self.CredentialInputValidation.verify_code_input_validation(
                code=code, email=email
            )
            # calling varify method
            email_key = self._generate_email_confirm_code_key(email=email)

            cache_code = self.CacheService.get(key=email_key)
            if not cache_code or str(cache_code) != str(code):
                return {"code": "invalid_code"}, 400

            # -------------Process new user---------------

            userdata_key = self._generate_user_process_queue_key(code=code)

            pending_userdata = json.loads(self.CacheService.get(key=userdata_key))
            if not pending_userdata:
                return {
                    "code": "failed",
                    "message": "Failed to complete process new user request!",
                }, 500

            process_new_user = self.process_new_user(userdata=pending_userdata)
            # -----------delete from cache ---------
            self.CacheService.delete(key=email_key)
            self.CacheService.delete(key=userdata_key)

            # -----------return -----------
            if not process_new_user:
                return {
                    "code": "failed",
                    "message": "Failed to complete process new user!",
                }, 500

            return {"code": "successfully", "message": "Successfully"}, 200
        except ValueError as e:
            return {"code": "missing_inputs", "message": str(e)}, 400
        except Exception as e:
            self._credential_logger().error(
                "Failed to complete code verify request", {e}
            )
            return {
                "code": "failed",
                "message": "Server failed to complete request",
            }, 500

    def process_new_user(self, userdata: dict):
        # assert(type(email) is not str,"Email should be string")
        try:
            display_name = userdata.get("display_name")
            username = userdata.get("username")
            password = userdata.get("password")
            email = userdata.get("email")

            res = self.UserDataBaseService.insert_new_userdata(
                email=email,
                username=username,
                display_name=display_name,
                password=password,
            )
            return res
        except ValueError as e:
            return False
