from datetime import datetime
from src.database.devices_database import DevicesDatabaseService
from src.trip_service.trip_service import ms_to_timestamptz
from src.utils.handle_exception import handle_exception
from src.server_config.service.input_validation import DeviceInputValidation
from src.types.device_types import DatabaseDevice, Device

class DevicesService:
    _instace = None
    _init = False

    def __new__(cls):
        if cls._instace is None:
            cls._instace = super().__new__(cls)
        return cls._instace

    def __init__(self):
        if self._init:
            return

        self.DevicesDatabase = DevicesDatabaseService()
        self.DeviceInputValidation = DeviceInputValidation()
        self._init = True


    @handle_exception("User Setting", "insert device")
    def insert_device(self,device:Device)->tuple[dict,int]:

        ## input validation
        self.DeviceInputValidation.device_input_validation(device_id=device.device_id,platform=device.platform,lastseen=device.last_seen)
        if device.push_token:
            self.DeviceInputValidation.push_token_input_validation(push_token=device.push_token)
        ## convert last_seen to date time
        formated_time = ms_to_timestamptz(device.last_seen)

        if not formated_time or not isinstance(formated_time,datetime):
            raise ValueError('Time not correctly formated')

        database_device = DatabaseDevice(user_id=device.user_id,device_id=device.device_id,push_token=device.push_token,platform=device.platform,last_seen=formated_time)
        ## insert into database
        insert = self.DevicesDatabase.insert_new_device(device=database_device)
        if not insert:
            return {'code':'failed','message':'Failed to insert new device'},500

        return {'code':'successfully'},200
