# purpose is to read/write trip domain
# trip domain

import json

from src.database.userdata_db_service import UserDataDataBaseService
from src.error_handler.error_handler import ErrorHandler
from src.utils.cache.cache import Cache
from src.utils.cache.keys.cache_keys import (
    GetBasicUserDataDomainCacheKey,
    GetUserDomainCacheKey,
)
from src.utils.time_convert import timestamptz_to_ms


class UserDataRepository:
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
        self.UserDataDatabaseService = UserDataDataBaseService()
        self.ErrorHandler = ErrorHandler().logger("User Repository")
        self._init = True

    def get_user_data(self, user_id: int):
        try:
            # get data from cache
            cache_key = GetUserDomainCacheKey(user_id=user_id)
            raw_data_from_cache = self.CacheService.get(key=cache_key)

            # load data into dict
            if raw_data_from_cache:
                data_from_cache = json.loads(raw_data_from_cache)
                return data_from_cache
            # cache miss
            user_data = self.UserDataDatabaseService.get_user_data_by_id(
                user_id=user_id
            )
            if not user_data:
                return None

            user_data["created_time"] = timestamptz_to_ms(user_data.get("created_time"))
            user_data["modified_time"] = timestamptz_to_ms(
                user_data.get("modified_time")
            )
            user_data["trips_modified_time"] = timestamptz_to_ms(
                user_data.get("trips_modified_time")
            )

            # put data to cache, 2hrs
            self.CacheService.set(key=cache_key, data=json.dumps(user_data), time=7200)
            return user_data
        except Exception as e:
            self.ErrorHandler.error("fail to get user data", str(e))
            print(e)
            return None

    # def get_user_basic_data(self, user_id: int):
    #     try:
    #         # get data from cache
    #         cache_key = GetBasicUserDataDomainCacheKey(user_id=user_id)
    #         raw_data_from_cache = self.CacheService.get(key=cache_key)

    #         # load data into dict
    #         if raw_data_from_cache:
    #             data_from_cache = json.loads(raw_data_from_cache)
    #             return data_from_cache
    #         # cache miss
    #         user_data = self.UserDataDatabaseService.get_user_basic_data_by_id(
    #             user_id=user_id
    #         )
    #         if not user_data:
    #             return None
    #         # put data to cache, 2hrs
    #         self.CacheService.set(key=cache_key, data=json.dumps(user_data), time=7200)
    #         return user_data
    #     except Exception as e:
    #         self.ErrorHandler.error("fail to get user data", str(e))
    #         print(e)
    #         return None

    def delete_user(self, user_id: int):
        try:
            delete_from_database = self.UserDataDatabaseService.delete_user_data(
                user_id=user_id
            )
            if not delete_from_database:
                return False
            return True
        except Exception as e:
            print(e)
            return False

    def invalidate_user_data_cache(self, user_id):
        try:
            cache_key = GetUserDomainCacheKey(user_id=user_id)
            self.CacheService.delete(key=cache_key)
        except Exception as e:
            self.ErrorHandler.error("fail to invalidate user data from cache", str(e))
            print(e)
