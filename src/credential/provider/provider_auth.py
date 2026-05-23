import json
import os
import uuid
from types import SimpleNamespace

# from falsk import requests
from google.auth.transport import requests
from google.oauth2 import id_token
from werkzeug.security import generate_password_hash

from src.credential.credential_base import CredentialBase

TOKENSTATUS = SimpleNamespace(
    PENDING="pending", VERIFIED="verified", COMPLETED="completed"
)
TOKENACTION = SimpleNamespace(
    RESET_PASSWORD="reset_password",
    SIGNUP_VIA_PROVIDER="signup_via_provider",
)


class ProviderAuth(CredentialBase):
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

    def _generate_pending_key(self, token: str) -> str:
        return f"new_user_pending_provider:token:{token}"

    def provider_verify(self, provider: str, token: str) -> tuple[dict, int]:
        # this function use to process signup or signin with provider

        try:
            # ------------Inputs validation-----------------------
            self.CredentialInputValidation.provider_input_validation(
                provider=provider, protiver_id=token
            )
            data_from_provider = None
            # verify id token based on provider
            # -------------------Request data from provider-------
            if provider == "google":
                data_from_provider = self._provider_verification_google(token=token)
                if not data_from_provider:
                    return {
                        "code": "failed_to_get_data_from_provider",
                        "message": "Failed to get data from provider, please try again or contact your provider!",
                    }, 400
                # data extract from provider
                email = data_from_provider["email"]
                provider_id = data_from_provider["provider_id"]
                user_data = self.UserDataBaseService.get_user_data_by_email(email=email)
            else:
                return {
                    "code": "provider_not_found",
                    "message": "Provider not found or currently not support!",
                }, 400
            # verified that email is active
            # ---------------------Sign up----------------------------
            if not user_data:
                # if user doesnt exists,
                # return request Sign up
                fields = {
                    "status": "pending",
                    "action": "signup_via_provider",
                    "email": email,
                    "provider_id": provider_id,
                    "provider": provider,
                }

                pending_token = str(uuid.uuid4())
                pending_key = self._generate_pending_key(token=pending_token)
                if not self.CacheService.set(
                    key=pending_key, data=json.dumps(fields), time=300
                ):
                    raise Exception("failed to handler pending")
                return {"code": "pending", "pending_token": pending_token}, 201
            # ---------------------Log in-----------------------------------
            # treat as signin, if it linked
            # if an account doesn't associate with the id provided and provider
            # we treated it at false even if there are account associate with the email
            if provider_id != user_data["provider_id"]:
                return ({"code": "failed", "message": "Account Not Linked"}), 400

            user_id = user_data["id"]
            role = user_data["role"]
            user_data = {"role": role, "user_id": user_id}
            # generate tokens
            token_data = self._jwt_cycle_handler(user_id=user_id, role=role)
            return {
                "code": "successfully",
                "tokens": token_data,
                "user_data": user_data,
            }, 200
        except ValueError as e:
            return {"code": "missing_inputs", "message": str(e)}, 400
        except Exception as e:
            self.errorHandler.logger("Auth").error(
                "failed to handler provider request", {e}
            )
            return {"code": "failed", "message": "Server Failed"}, 500

    def provider_signup_complete(
        self, token: str, display_name: str, username: str, password: str
    ) -> tuple[dict, int]:
        try:
            assert token, "Pending token not found"
            # ---------------Get data from cache----------
            pending_key = self._generate_pending_key(token=token)
            pending_userdata = self.CacheService.get(key=pending_key)
            if not pending_userdata:
                return {
                    "code": "not_found",
                    "message": "Request user not found or expired!",
                }, 400

            pending_userdata = json.loads(pending_userdata)
            email = pending_userdata.get("email")
            provider = pending_userdata.get("provider")
            provider_id = pending_userdata.get("provider_id")
            # -----------------------Input validation-----------------
            self.CredentialInputValidation.signup_input_validation(
                username=username,
                password=password,
                display_name=display_name,
                email=email,
            )
            self.CredentialInputValidation.provider_input_validation(
                protiver_id=provider_id, provider=provider
            )
            # checking again for exists email
            # ----------------------Email Check------------------------
            if self.UserDataBaseService.get_user_data_by_email(email=email):
                return {
                    "code": "email_exists",
                    "message": "Email aldready associate with an account!",
                }, 400

            ## if the username already exists in database, return
            # ---------------------Username Check------------------------
            if self.UserDataBaseService.get_user_data_by_username(user_name=username):
                return {
                    "code": "username_exists",
                    "message": "Username aldready exists, please choose a different name",
                }, 400
            hashed_password = generate_password_hash(password=password)
            # put inside the database
            # ---------------------Insert----------------------------
            insert_userdata = (
                self.UserDataBaseService.insert_new_user_with_provider_data(
                    email=email,
                    display_name=display_name,
                    username=username,
                    password=hashed_password,
                    provider=provider,
                    provider_id=provider_id,
                )
            )
            if not insert_userdata:
                raise Exception("failed")
            # ------------------Clean up---------------------------
            self.CacheService.delete(key=pending_key)

            return {"code": "successfully", "message": "Successfully"}, 200
        except AssertionError as e:
            return {"code": "missing_inputs", "message": str(e)}, 400

        except ValueError as e:
            return {"code": "missing_inputs", "message": str(e)}, 400
        except Exception as e:
            self.errorHandler.logger("Auth").error(
                "failed to handler provider request", {e}
            )
            return {"code": "failed", "message": "Server Failed"}, 500

    def _provider_verification_google(self, token: str) -> dict:
        # manually try client_ids
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
