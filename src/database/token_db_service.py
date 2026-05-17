from datetime import datetime
from time import time, timezone
from typing import Any

from psycopg2.extras import RealDictRow

from src.database.database import Database
from src.database.database_keys import DATABASEKEYS
from trip_service.trip_service import timestamptz_to_ms


class TokenDatabaseService(Database):
    _instance = None
    _init = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init:
            return
        super().__init__()
        self._init = True

    def verify_refresh_token(self, refresh_token: str) -> bool:
        row = self.find_item_in_sql(
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
        format_expired_at = timestamptz_to_ms(int(expired_at))

        if int(time.time() * 1000) >= format_expired_at:
            self.revoke_refresh_token(user_id=row["user_id"])
            return False

        return True

    def revoke_refresh_token(self, user_id: str) -> bool:
        """
        Mark a refresh token as revoked in the database.

        Args:
            user_id (int): The user's ID whose token should be revoked.
        """
        status = self.update_db(
            table=DATABASEKEYS.TABLES.TOKENS,
            item=DATABASEKEYS.TOKENS.USER_ID,
            value=user_id,
            item_to_update=DATABASEKEYS.TOKENS.REVOKED,
            value_to_update=True,
        )
        return status
