# purpose is to read/write trip domain
# trip domain

import json

from src.database.friendships_db_service import FriendShipsDatabaseService
from src.database.tripdata_db_service import TripDataBaseService
from src.error_handler.error_handler import ErrorHandler
from src.utils.cache.cache import Cache
from src.utils.cache.keys.cache_keys import (
    GetFriendshipCacheKey,
    GetUserRelationshipsDomainCacheKey,
)
from src.utils.time_convert import timestamptz_to_ms


class FriendShipsRepository:
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
        self.FriendshipsDatabaseService = FriendShipsDatabaseService()
        self.ErrorHandler = ErrorHandler().logger("Friendships repository")
        self._init = True

    def get_user_relationships(self, user_id: int):
        try:
            cache_key = GetUserRelationshipsDomainCacheKey(user_id=user_id)
            raw_data_from_cache = self.CacheService.get(key=cache_key)
            if raw_data_from_cache:
                data_from_cache = json.loads(raw_data_from_cache)
                return data_from_cache
            relationships = self.FriendshipsDatabaseService.get_user_relationships(
                user_id=user_id
            )
            for relationship in relationships:
                relationship["last_update"] = timestamptz_to_ms(
                    relationship["last_update"]
                )
                relationship = dict(relationship)

            self.CacheService.set(
                key=cache_key, data=json.dumps(relationships), time=7200
            )
            return relationships
        except Exception as e:
            print(e)
            self.ErrorHandler.error("fail to get user relation domain", str(e))
            return None

    def get_relationship(self, user_id1: int, user_id2: int):
        try:
            ## look into cache
            cache_key = GetFriendshipCacheKey(user_id1=user_id1, user_id2=user_id2)
            raw_data_from_cache = self.CacheService.get(key=cache_key)
            if raw_data_from_cache:
                data_from_cache = json.loads(raw_data_from_cache)
                return data_from_cache
            ## Cache miss
            relationship = self.FriendshipsDatabaseService.get_relationship(
                user_id1=user_id1, user_id2=user_id2
            )
            if relationship is None:
                return None
            ## set new cache
            self.CacheService.set(
                key=cache_key, data=json.dumps(relationship), time=7200
            )
            return dict(relationship)
        except Exception as e:
            print(e)
            self.ErrorHandler.error("failed to get relationship", str(e))
            return None

    def invalidate_cache(self, user_id: int):
        try:
            cache_key = GetUserRelationshipsDomainCacheKey(user_id=user_id)
            self.CacheService.delete(key=cache_key)
        except Exception as e:
            print(e)
            self.ErrorHandler.error("failed invalidate cache", str(e))
