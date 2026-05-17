import os
from datetime import datetime, timedelta, timezone

from src.error_code.error_code import INPUT_ERROR
from src.token.tokenservice import TokenService


class CredentialBase:
    _instance = None
    _init = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._init:
            return
        self.TokenService = TokenService()
        self._init = True

    def _email_verify(self, email: str):
        if not self.inputValidationService.email_validation(email=email):
            return False, INPUT_ERROR.EMAIL
        exists = self.UserDatabaseService.get_user_data_by_email(email=email)
        if exists:
            return False, "email_exists"
        return True, "successfully"

    def _jwt_cycle_handler(self, user_id: int, role: str):
        # old token got revoked
        self.TokenService.revoke_refresh_token(user_id=user_id)

        # new tokens generated
        refresh_token = self.TokenService.generate_jwt(
            fields={"user_id": user_id, "role": role}, exp_time={"days": 30}
        )
        access_token = self.TokenService.generate_jwt(
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
