# this is wrapper layer, it purpose is only be a caller for database. Best is to not compute any business logic in this layer


from datetime import datetime

from src.database.database import Database
from src.database.database_keys import DATABASEKEYS
from src.error_handler.error_handler import ErrorHandler
from src.types.device_types import DatabaseDevice


class DevicesDatabaseService(Database):
    _instance = None
    _init = False

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init:
            return
        super().__init__()
        self.ErrorHandler = ErrorHandler().logger("Friendship Database Service")
        self._init = True

    def insert_new_device(self,device:DatabaseDevice):
        con,cur = self.connect_db()
        try:
            cur.execute(
                f"""INSERT INTO {DATABASEKEYS.TABLES.DEVICES} (
                        {DATABASEKEYS.DEVICES.USER_ID},
                        {DATABASEKEYS.DEVICES.DEVICE_ID},
                        {DATABASEKEYS.DEVICES.TOKEN},
                        {DATABASEKEYS.DEVICES.PLATFORM},
                        {DATABASEKEYS.DEVICES.LAST_SEEN})
                        VALUES ( %s, %s, %s, %s, %s)""",
                (
                    device.user_id,
                    device.device_id,
                    device.token,
                    device.platform,
                    device.last_seen
                ),
            )
            con.commit()
            self.close_db(conn=con)
            if cur.rowcount >= 1:
                return True
            return False
        except Exception as e:
            print(e)
            self.ErrorHandler.error('failed to insert device',str(e))
        finally:
            self.close_db(conn=con)

    def get_user_devices(self,user_id:int):
        devices = self.find_item_in_sql(table={DATABASEKEYS.TABLES.DEVICES}, item={DATABASEKEYS.DEVICES.USER_ID}, value=user_id,return_option='fetchall')
        return devices
