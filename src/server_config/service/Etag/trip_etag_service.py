from werkzeug.http import generate_etag
from src.server_config.service.cache import Cache
from src.database.trip_db_service import TripDatabaseService
from src.server_config.service.Etag.Etag import EtagService
import json
from src.database.database_keys import DATABASEKEYS
class TripEtagService(EtagService):
    _instance = None
    _init = False
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if TripEtagService._init:return
        super().__init__()
        self.trip_database_service = TripDatabaseService()
        TripEtagService._init = True

    def get_all_trip_etag_key(self,user_id:int):
        return f'user{user_id}:alltrips'
    
    def get_trip_etag_key(self,user_id:int,trip_id:int):
        return f'user{user_id}:trip:{trip_id}'
    
    def get_all_trip_etag_data_string(self, user_id:int,version:int):
        return f'user{user_id}:alltrips:version{version}'
        
    def get_trip_etag_data_string(self,user_id,trip_id,version):
        return f'user{user_id}:trip:{trip_id}:version:{version}'
    
    
    def refresh_user_trips_etag(self,user_id):
        etag_key = self.get_all_trip_etag_key(user_id=user_id)
        # delete old etag from cache
        self.cacheService.delete(etag_key)
        
        # update the version 
        self.trip_database_service.update_all_trips_version(user_id=user_id)
        
        # new new etag
        new_version = self.trip_database_service.get_user_trips_data(user_id=user_id,data_type=DATABASEKEYS.USERDATA.TRIPDATA_VERSION)
        new_etag_data = self.get_all_trip_etag_data_string(user_id=user_id,version=new_version)
        new_etag = self.generate_etag(key=new_etag_data)
        
        # push new etag into db
        self.trip_database_service.update_db(table=DATABASEKEYS.TABLES.USERDATA,item=DATABASEKEYS.USERDATA.USER_ID,value=user_id,
                                                item_to_update=DATABASEKEYS.USERDATA.TRIPS_DATA_ETAG,value_to_update=new_etag)
        
        # push new etag into cache 
        self.cacheService.set(key=etag_key,time=3600,data=new_etag)
        