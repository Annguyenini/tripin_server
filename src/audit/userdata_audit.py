from src.audit.audit_actions import USERAUDIT
from src.database.database import Database
from src.database.database_keys import DATABASEKEYS
from src.error_handler.error_handler import ErrorHandler


class UserdataAudit:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.databaseService = Database()
        self.ErrorHandler = ErrorHandler().logger("UserDataAudit")
        pass

    def _update_user_audit(
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
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (user_id, modified_time, action, ip_address, old_value, new_value),
            )
            con.commit()
            return True if cur.rowcount > 0 else False
        except ConnectionError as ce:
            self.ErrorHandler.error(
                "failed to update userdata audit, connection error: ", {str(ce)}
            )
            False
        except Exception as e:
            self.ErrorHandler.error("failed to update userdata audit: ", {e})
            return False
        finally:
            self.databaseService.close_db(conn=con)

    def change_user_avatar_audit(
        self,
        user_id: str,
        modified_time: str,
        ip_address: str,
        old_value: str,
        new_value: str,
    ) -> bool:
        return self._update_user_audit(
            user_id=user_id,
            modified_time=modified_time,
            action=USERAUDIT.ACTIONS.CHANGE_AVATAR,
            ip_address=ip_address,
            old_value=old_value,
            new_value=new_value,
        )
