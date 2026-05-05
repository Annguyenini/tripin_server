from src.database.database import Database
from src.database.database_keys import DATABASEKEYS


class UserdataAudit:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.databaseService = Database()
        pass

    def update_user_audit(
        self,
        user_id: int,
        modified_time: str,
        action: str,
        ip_address: str,
        old_value: str,
        new_value: str,
    ):
        con, cur = self.databaseService.connect_db()
        try:
            cur.execute(
                f"""
                INSERT INTO {DATABASEKEYS.TABLES.USER_AUDIT}(
                {DATABASEKEYS.USER_AUDIT.USER_ID},
                {DATABASEKEYS.USER_AUDIT.MODIFIED_TIME},
                {DATABASEKEYS.USER_AUDIT.ACTION},
                {DATABASEKEYS.USER_AUDIT.IP_ADDRESS},
                {DATABASEKEYS.USER_AUDIT.OLD_VALUE},
                {DATABASEKEYS.USER_AUDIT.NEW_VALUE}
                )
                """,
                (user_id, modified_time, action, ip_address, old_value, new_value),
            )
            con.commit()
            return True if cur.rowcount > 0 else False
        except ConnectionError as ce:
            pass
        except Exception as e:
            return False
        finally:
            self.databaseService.close_db(conn=con)
