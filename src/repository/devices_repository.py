# purpose is to read/write trip domain
# trip domain

import json

from src.database.devices_database import DevicesDatabaseService
from src.database.friendships_db_service import FriendShipsDatabaseService
from src.database.tripdata_db_service import TripDataBaseService
from src.error_handler.error_handler import ErrorHandler
from src.utils.cache.cache import Cache
from src.utils.cache.keys.cache_keys import (
    GetFriendshipCacheKey,
    GetUserRelationshipsDomainCacheKey,
)
from src.utils.time_convert import timestamptz_to_ms


class DevicesRepository:
    _instance = None
    _init = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init:
            return
        self.CacheService = Cache()
        self.DevicesDatabaseService = DevicesDatabaseService()
        self.ErrorHandler = ErrorHandler().logger("Devices repository")
        self._init = True

    def get_devices_from_user(self,user_id:int):
        devices = self.DevicesDatabaseService.get_user_devices(user_id=user_id)
        return devices
