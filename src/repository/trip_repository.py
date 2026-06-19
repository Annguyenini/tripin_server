# purpose is to read/write trip domain
# trip domain

import json

from src.database.tripdata_db_service import TripDataBaseService
from src.utils.cache.cache import Cache
from src.utils.cache.keys.cache_keys import (
    GetTripDataCacheKey,
    GetTripDomainCacheKey,
    GetUserTripsDataCacheKey,
    GetUserTripsDomainCacheKey,
)
from src.utils.time_convert import timestamptz_to_ms


class TripRepository:
    _instance = None
    _init = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init:
            return
        self.TripDatabaseService = TripDataBaseService()
        self.CacheService = Cache()
        self._init = True

    def get_trip_data(self, trip_id: int):
        try:
            if not trip_id:
                raise ValueError("invalid trip_id")
            # ----------------------------cache check ----------------------------
            trip_domain_cache_key = GetTripDomainCacheKey(trip_id=trip_id)
            data_from_cache_raw = self.CacheService.get(key=trip_domain_cache_key)
            if data_from_cache_raw:
                data_from_cache = json.loads(data_from_cache_raw)
                return data_from_cache
            # ----------------------------Cache Miss --------------------------------
            trip_data_row = self.TripDatabaseService.get_trip_data_from_trip_id(
                trip_id=trip_id
            )
            if trip_data_row is None:
                return None
            trip_data_row["created_time"] = timestamptz_to_ms(
                trip_data_row["created_time"]
            )
            trip_data_row["ended_time"] = timestamptz_to_ms(trip_data_row["ended_time"])
            trip_data_row["content_modified_time"] = timestamptz_to_ms(
                trip_data_row["content_modified_time"]
            )
            trip_data_row["modified_time"] = timestamptz_to_ms(
                trip_data_row["modified_time"]
            )
            # ----------------------------- Set Cache-----------------------------------
            self.CacheService.set(
                key=trip_domain_cache_key, time=7200, data=json.dumps(trip_data_row)
            )
            return trip_data_row
        except Exception as e:
            print(e)
            return None

    def get_all_trip_data(self, user_id: int) -> list[dict]:
        try:
            if not user_id:
                raise ValueError("invalid user_id")
            # ----------------------------cache check ----------------------------
            all_trip_cache_key = GetUserTripsDomainCacheKey(user_id=user_id)
            data_from_cache_raw = self.CacheService.get(key=all_trip_cache_key)
            if data_from_cache_raw:
                data_from_cache = json.loads(data_from_cache_raw)

                return data_from_cache
            # ----------------------------Cache Miss --------------------------------
            trips_data_row = self.TripDatabaseService.get_all_trips_from_user_id(
                user_id=user_id
            )
            if trips_data_row is None:
                return None
            for trip_data_row in trips_data_row:
                trip_data_row["created_time"] = timestamptz_to_ms(
                    trip_data_row["created_time"]
                )
                trip_data_row["ended_time"] = timestamptz_to_ms(
                    trip_data_row["ended_time"]
                )
                trip_data_row["content_modified_time"] = timestamptz_to_ms(
                    trip_data_row["content_modified_time"]
                )
                trip_data_row["modified_time"] = timestamptz_to_ms(
                    trip_data_row["modified_time"]
                )
            # ----------------------------- Set Cache-----------------------------------
            self.CacheService.set(
                key=all_trip_cache_key, time=7200, data=json.dumps(trips_data_row)
            )
            return trips_data_row
        except Exception as e:
            print(e)
            return None

    def invalidate_trip_cache(self, trip_id: int):
        try:
            self.CacheService.delete(key=GetTripDomainCacheKey(trip_id=trip_id))
        except Exception as e:
            raise str(e)

    def invalidate_user_trips_cache(self, user_id: int):
        try:
            self.CacheService.delete(key=GetUserTripsDomainCacheKey(user_id=user_id))
        except Exception as e:
            raise str(e)
