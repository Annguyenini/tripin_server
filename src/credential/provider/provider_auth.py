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
        if not self._initialize:
            self._initialize = True

    def provider_verify(self, provider: str, token: str):
        # 2 in 1, sigup or singin
        # input validation
        try:
            self.CredentialInputValidation.provider_input_validation(
                provider=provider, protiver_id=token
            )
            data_from_provider = None
            # verify id token based on provider
            if provider == "google":
                data_from_provider = self._provider_verification_google(token=token)
                if not data_from_provider:
                    return False, {"code": "notfound"}
                # data extract from provider
                email = data_from_provider["email"]
                name = data_from_provider["name"]
                provider_id = data_from_provider["provider_id"]
                user_data = self.UserDataBaseService.get_user_data_by_email(email=email)
            else:
                return {"code": "failed", "message": "Unkown Provider"}
            # verified that email is active

            if not user_data:
                # if user doesnt exists,
                # return request Sign up
                email_verify, code = self._email_verify(email=email)
                if not email_verify:
                    return False, {"code": code}
                    # token containt email,sub(provider_id),name,provider
                    # token will been use for complete sign up form

                pending_token = self.TokenService.generate_jwt(
                    fields={
                        "status": "pending",
                        "action": "signup_via_provider",
                        "email": email,
                        "provider_id": provider_id,
                        "provider": provider,
                        "name": name,
                    }
                )
                return True, {"code": "pending", "pending_token": pending_token}

            # treat as signin, if it linked
            # if an account doesn't associate with the id provided and provider
            # we treated it at false even if there are account associate with the email
            if provider_id != user_data["provider_id"]:
                return False, ({"code": "failed", "message": "Account Not Linked"})

            user_id = user_data["id"]
            role = user_data["role"]
            user_data = {"role": role, "user_id": user_id}
            # generate tokens
            token_data = self._jwt_cycle_handler(user_id=user_id, role=role)
            return True, {
                "code": "successfully",
                "tokens": token_data,
                "user_data": user_data,
            }
        except ValueError as e:
            return {"code": "missing_inputs", "message": "Missing inputs"}
        except Exception as e:
            self.errorHandler.logger("Auth").error(
                "failed to handler provider request", {e}
            )
            return False, {"code": "failed", "message": "Server Failed"}

    def provider_signup_complete(
        self, token: str, display_name: str, username: str, password: str
    ):
        try:
            # input validation
            if not self.inputValidationService.username_validation(username=username):
                return False, INPUT_ERROR.USERNAME
            if not self.inputValidationService.displayname_validation(
                display_name=display_name
            ):
                return False, INPUT_ERROR.DISPLAY_NAME
            if not self.inputValidationService.password_validation(password=password):
                return False, INPUT_ERROR.PASSWORD
            # decode token
            data_from_token = self.tokenService.decode_jwt(
                token=token,
                fields=["email", "provider", "provider_id", "action", "status"],
            )
            # token guard
            if (
                not data_from_token
                or data_from_token["action"] != TOKENACTION.SIGNUP_VIA_PROVIDER
                or data_from_token["status"] != TOKENSTATUS.PENDING
            ):
                return False, {"code": "invalid_token"}
            email = data_from_token["email"]
            provider = data_from_token["provider"]
            provider_id = data_from_token["provider_id"]
            # checking again for exists email
            if self.UserDatabaseService.get_user_data_by_email(email=email):
                return False, {
                    "code": "email_exists",
                    "message": "Email aldready associate with an account!",
                }

            ## if the username already exists in database, return
            if self.UserDatabaseService.get_user_data_by_username(user_name=username):
                return False, {
                    "code": "username_exists",
                    "message": "Username aldready exists, please choose a different one",
                }
            hashed_password = generate_password_hash(password=password)
            # put inside the database
            insert_userdata = self.UserDatabaseService.insert_new_userdata(
                email=email,
                display_name=display_name,
                username=username,
                password=hashed_password,
            )
            insert_provider = self.UserDatabaseService.insert_user_provider_data(
                provider=provider, provider_id=provider_id
            )
            if not insert_userdata or insert_provider:
                return False, {"code": "failed", "message": "Server Failed"}

            return True, {"code": "successfully", "message": "Successfully"}
        except Exception as e:
            self.errorHandler.logger("Auth").error(
                "failed to handler provider request", {e}
            )
            return False, {"code": "failed", "message": "Server Failed"}

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
