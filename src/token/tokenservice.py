from dataclasses import field
from datetime import datetime, timedelta, timezone

import jwt

from src.database.database import Database
from src.database.database_keys import DATABASEKEYS
from src.server_config.config import Config


class TokenService:
    def __init__(self):
        self.db = Database()
        self.config = Config()

    def get_current_time(self) -> int:
        return int(datetime.now(timezone.utc).timestamp())

    def generate_jwt(self, fields: object, exp_time: dict = {}) -> str | None:
        if not exp_time:
            exp_time = {"days": 30}

        SECRET_KEY = self.config.private_key
        if not SECRET_KEY:
            return None
        if not fields:
            return None
        payload = {
            **fields,
            "exp": int(
                (datetime.now(timezone.utc) + timedelta(**exp_time)).timestamp()
            ),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="RS256")

        assert token is not None, "Token is undefined!"
        return token

    def decode_jwt(self, token: str, fields: list[str]) -> dict:
        """
        Decode a JWT token and extract payload data.

        Args:
            token (str): The access token.

        Returns:
            dict: Extracted user_id and role from the token payload.
        """
        assert token is not None, "Token is None!"
        try:
            PUBLIC_KEY = self.config.public_key
            if not PUBLIC_KEY:
                return {}
            payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
            result = {}
            for field in fields:
                result[field] = payload[field]
            return result
        except Exception as e:
            return {}

    def jwt_verify(self, token: str) -> tuple[bool, str, str]:
        """
        Verify a JWT access token.

        Args:
            token (str): The access token.

        Returns:
            tuple: (status: bool, message: str, code: str)
        """
        PUBLIC_KEY = self.config.public_key
        if not PUBLIC_KEY:
            return {}
        try:
            payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
            if self.get_current_time() > int(payload["exp"]):
                return False, "Token Expired!", "token_expired"

        except jwt.ExpiredSignatureError:
            return False, "Token Expired!", "token_expired"

        except jwt.InvalidTokenError:
            return False, "Token Invalid!", "token_invalid"

        return True, "Successfully!", "successfully"

    def refresh_token_verify(self, refresh_token: str) -> bool:
        """
        Verify a refresh token against the database.

        Args:
            refresh_token (str): The refresh token.

        Returns:
            bool: True if valid, False otherwise.
        """
        row = self.db.find_item_in_sql(
            table=DATABASEKEYS.TABLES.TOKENS,
            item=DATABASEKEYS.TOKENS.TOKEN,
            value=refresh_token,
        )

        if row is None:
            return False

        revoked_status = row["revoked"]
        assert isinstance(revoked_status, bool), "revoked_status must be of type bool"

        if revoked_status:
            return False

        expired_at = row["expired_at"]

        if expired_at.tzinfo is None:
            expired_at = expired_at.replace(tzinfo=timezone.utc)

        if datetime.now(timezone.utc) >= expired_at:
            print("wrong", refresh_token, datetime.now(timezone.utc), expired_at)
            self.revoke_refresh_token(user_id=row["user_id"])
            return False

        return True

    def revoke_refresh_token(self, user_id) -> None:
        """
        Mark a refresh token as revoked in the database.

        Args:
            user_id (int): The user's ID whose token should be revoked.
        """
        status = self.db.update_db(
            table=DATABASEKEYS.TABLES.TOKENS,
            item=DATABASEKEYS.TOKENS.USER_ID,
            value=user_id,
            item_to_update=DATABASEKEYS.TOKENS.REVOKED,
            value_to_update=True,
        )
        assert status is True, "Error updating database: failed to revoke token"

    def request_new_access_token(self, refresh_token: str) -> tuple[bool, str | None]:
        """
        Issue a new access token using a valid refresh token.

        Args:
            refresh_token (str): The refresh token.

        Returns:
            tuple: (success: bool, new_access_token: str | None)
        """
        if not self.refresh_token_verify(refresh_token):
            return False, None

        data = self.decode_jwt(refresh_token, fields=["user_id", "role"])
        field = {"user_id": data["user_id"], "role": data["role"]}
        new_token = self.generate_jwt(fields=field, exp_time={"minutes": 15})

        return True, new_token
