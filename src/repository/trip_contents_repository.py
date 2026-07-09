# purpose is to read/write trip domain
# trip domain

import json

from src.repository.trip_repository import TripRepository
from src.database.trip_content_db_service import TripContentsDatabaseService
from src.database.tripdata_db_service import TripDataBaseService
from src.utils.cache.cache import Cache
from src.utils.cache.keys.cache_keys import (
    GetTripContentsDomainCacheKey,
    GetTripDataCacheKey,
    GetTripDomainCacheKey,
    GetUserTripsDataCacheKey,
    GetUserTripsDomainCacheKey,
)
from src.utils.time_convert import timestamptz_to_ms


class TripContentsRepository:
    _instance = None
    _init = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init:
            return
        self.TripContentsDatabaseService = TripContentsDatabaseService()
        self.CacheService = Cache()
        self.TripRepository = TripRepository()
        self._init = True

    def get_trip_content(self, trip_id: int):
        # ----------------------data from cache------------------------
        cache_key = GetTripContentsDomainCacheKey(trip_id=trip_id)
        raw = self.CacheService.get(key=cache_key)
        trip_data = self.TripRepository.get_trip_data(trip_id=trip_id)
        if raw:
            return json.loads(raw)
        # ----------------------cache miss------------------------------
        contents = self.TripContentsDatabaseService.get_all_trip_content_cards(
            trip_id=trip_id
        )
        if contents is None:
            return None
        for content in contents:
            # convert timestamp to ms
            content['trip_name']=trip_data.get('trip_name')
            content["time_stamp"] = timestamptz_to_ms(timestamp=content["time_stamp"])
            content["modified_time"] = timestamptz_to_ms(
                timestamp=content["modified_time"]
            )
        # -------------------------set to cache---------------------------
        self.CacheService.set(key=cache_key, time=7200, data=json.dumps(contents))

        return contents

    def invalid_trip_contents_cache(self, trip_id: int):
        cache_key = GetTripContentsDomainCacheKey(trip_id=trip_id)
        self.CacheService.delete(key=cache_key)
