import json
import secrets
import uuid
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from src.credential.credential_base import CredentialBase


class ResetPasswordService(CredentialBase):
    _instance = None
    _initialize = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialize:
            return
        super().__init__()
        self._initialize = True

    def _generate_reset_password_process_key(self, token: str) -> str:
        return f"reset_password:token:{token}"

    def _generate_email_confirm_code_key(self, code: str) -> str:
        return f"reset_password:code:{code}"

    def request_reset_password(self, email: str) -> tuple[dict | None, int]:
        # phase 1
        # Diagram can be found in /artitecture/diagrams
        try:
            # verify email if it in the database
            # -----------input validation-------------------
            self.CredentialInputValidation.email_validation(email=email)

            # ---------------Email varification------------------
            # check if email associate with an account
            userdata = self.UserDataBaseService.get_user_data_by_email(email=email)
            if not userdata:
                return {"code": "email_not_exists"}, 404
            email = userdata["email"]
            # ------Generate code and send code-----------------
            random_code = secrets.randbelow(900000) + 100000
            confirmation_key = self._generate_email_confirm_code_key(code=random_code)
            self.CacheService.set(
                key=confirmation_key, data=json.dumps({"email": email}), time=300
            )
            send_code = self.CredentialEmailService.send_email_confirmation_code(
                code=random_code, recipient=email
            )
            if not send_code:
                return {"code": "server_failed", "token": None}, 500
            return {
                "code": "pending",
            }, 201
        except ValueError as e:
            return {"code": "missing_inputs", "message": str(e)}
        except Exception as e:
            self.errorHandler.logger("Auth").error(
                "Failed at request reset password", {e}
            )
            return {"code": "server_failed", "token": None}, 500

    def request_reset_password_verify(
        self, code: int, email: str
    ) -> tuple[bool, dict, int]:
        # phase 2
        # Diagram can be found in /artitecture/diagrams

        # guard
        try:
            # ----------Guard-----------
            assert code, "Missing code"
            assert email, "Missing Email, please redo the process!"
            # ----------Check in cache-------------------------
            confirmation_key = self._generate_email_confirm_code_key(code=str(code))
            result_from_cache = json.loads(self.CacheService.get(key=confirmation_key))
            if not result_from_cache:
                return {"code": "failed", "Message": "Code Not Correct!"}, 400
            # ---------------Verify email -----
            email_from_cache = result_from_cache["email"]
            if not email_from_cache or str(email_from_cache) != email:
                return {"code": "email_not_match", "message": "Email not match!"}, 400

            # --------------generate token-----
            # return for next step
            verified_token = str(uuid.uuid4())
            verified_key = self._generate_reset_password_process_key(
                token=verified_token
            )

            # _________put verify token ---------
            if not self.CacheService.set(
                key=verified_key, data=json.dumps({"email": email}), time=300
            ):
                return {"code": "failed", "message": "server failed"}, 500

            # ---------delete verify code--------
            self.CacheService.delete(key=confirmation_key)

            return {"token": verified_token, "code": "verified"}, 201
        except AssertionError as e:
            return {"code": "missing_inputs", "message": str(e)}, 400
        except Exception as e:
            self.errorHandler.logger("Auth").error(
                "Failed at reset password verify", {e}
            )
            return {}, 500

    def reset_password_handler(
        self, token: str, email: str, new_password: str, ip_address: str
    ) -> tuple[dict, int]:
        try:
            # ---------------Token/ Email Checking---------------
            process_key = self._generate_reset_password_process_key(token=token)
            result_from_cache = self.CacheService.get(key=process_key)

            if not result_from_cache:
                return {
                    "code": "invalid_token",
                    "message": "There are a problem occur with your session! \n Please try again!",
                }, 400
            # guard
            result_from_cache = json.loads(result_from_cache)
            if result_from_cache["email"] != email:
                return {
                    "code": "invalid_email",
                    "message": "There are a problem occur with your session! \n Please try again!",
                }, 400
            #
            # -----------------------New password validation-----------------
            self.CredentialInputValidation.password_validation(password=new_password)

            # old data , old password we could enforce new password != old password in the future
            userdata = self.UserDataBaseService.get_user_data_by_email(email=email)
            user_id = userdata.get("id")
            print(userdata)
            old_password = userdata["password"]
            # -----------------------generate new hased passwords-----
            new_hased_password = generate_password_hash(password=new_password)
            # ---------------------Update new password--------------
            update = self.UserDataBaseService.update_user_password(
                user_id=user_id, new_hashed_password=new_hased_password
            )
            # ---------------------Delete token from cache----------
            self.CacheService.delete(key=process_key)
            # ---------------------Audit-----------------------
            # audit
            self.UserdataAudit._update_user_audit(
                user_id=user_id,
                modified_time=datetime.now(),
                action="reset_password",
                ip_address=ip_address,
                old_value=old_password,
                new_value=new_hased_password,
            )
            if not update:
                return {
                    "code": "server_failed",
                    "massage": "failed to reset your password, Please try again later!",
                }, 500
            return {
                "code": "successfully",
                "message": "Your password is successfully change!",
            }, 200
            pass
        except Exception as e:
            self.errorHandler.logger("Auth").error("Failed at reset password", {e})
            return {
                "code": "failed",
                "message": "Server failed to complete request, Please try again!",
            }, 500
            pass
