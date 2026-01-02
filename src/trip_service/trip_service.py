from src.token.tokenservice import TokenService
from src.database.database import Database
from src.database.s3.s3_service import S3Sevice
from src.database.s3.s3_dirs import TRIP_DIR
from src.database.trip_db_service import TripDatabaseService
from src.server_config.service.cache import Cache
from src.server_config.service.Etag.Etag import EtagService
import psycopg2
from datetime import datetime
import json
class TripService:
    _instance = None
    _init = False
    def __new__(cls,*args,**kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    def __init__(self):
        if not self._init: 
            self.token_service = TokenService()
            self.database_service = Database()
            self.trip_database_service = TripDatabaseService()
            self.s3_service = S3Sevice()
            self.etag_service = EtagService()
            self.cache_service = Cache()
            self._init =True
    
    def process_new_trip(self,user_id,trip_name,imageUri:str = None):
        # trip_db layout 
        # trip_id | trip_name | user_id | start_time | end_time | active

        ##return if user are currently in another aactive 
        exist_trip = self.database_service.find_item_in_sql(table="tripin_trips.trips_table",item="user_id",value=user_id,
                                                            second_condition=True,second_item="active",second_value=True )

        if exist_trip is not None:
            return False, f"Currently in {exist_trip["trip_name"]}",None
    
        ##return if exists trip name from user
        exist_trip_name = self.database_service.find_item_in_sql(table = "tripin_trips.trips_table", item = "trip_name", value = trip_name,second_condition=True, second_item="user_id",second_value=user_id)

        if exist_trip_name is not None:
            return False, f"Trip name: {trip_name} already exist!",None
        
        
        ##process to create new trip
        create_trip,trip_id = self.trip_database_service.insert_to_database_trip(user_id = user_id, trip_name = trip_name,imageUri=imageUri)
        if create_trip:
            return True, f"Created trip {trip_name} successfully", trip_id
        else: 
            return False, "Error occur while creating trip.",None
           
           
  
    def end_a_trip(self, trip_id:int):
        # print(trip_id
        update_trip_status = self.database_service.update_db(table = "tripin_trips.trips_table", item = "id", value= trip_id, item_to_update = "active",value_to_update = False)
        if not update_trip_status:
            return False, f"Error while trying to end trip {trip_id}"
        update_trip_ended_time = self.database_service.update_db(table = "tripin_trips.trips_table", item="id", value= trip_id ,item_to_update="ended_time",value_to_update=datetime.now())
        if not update_trip_ended_time:
            return False, f"Error while trying to end trip {trip_id}"
        return True,f"Successfully end trip {trip_id}" 
    
    def get_trip_data(self,user_id,client_etag):
        """_summary_

        Args:
            user_id (_type_): _description_
            etag (_type_): _description_
        """
        
        etag_key =f'user{user_id}_curr_trip_etag'
        # fetch the etag from cache if match return        
        etag_from_cache = self.cache_service.get(etag_key)
        if client_etag == etag_from_cache:
            return None, client_etag
        
        # fetch user current trip 
        trip_data_row = self.database_service.find_item_in_sql('tripin_trips.trips_table','user_id',user_id,True,'active',True)
        # if doesnt exist return
        if trip_data_row is None :
            return None,None
        # get etag from bd
        db_etag = trip_data_row['etag']
        if client_etag == db_etag:
            self.cache_service.set(etag_key,3600,client_etag)
            return None, client_etag
        
        # data object
        trip_id = trip_data_row['id']
        trip_name = trip_data_row['trip_name']
        created_timestamp = trip_data_row['created_time']
        created_time = int(created_timestamp.timestamp() * 1000)
        trip_image_default = trip_data_row['image']
        
        trip_image = None
        if trip_image_default:
            trip_image = self.s3_service.generate_temp_uri(trip_image_default)
        
        
        
        trip_data = {'etag_status':'failed','trip_id':trip_id,'trip_name':trip_name,'created_time':created_time,'trip_image':trip_image if trip_image else None}
        
        # generate new etag
        new_etag = self.etag_service.generate_Etag_from_object(data=trip_data)
        # add to cache
        self.cache_service.set(key=etag_key,time=3600,data=new_etag)
        return trip_data, new_etag
    
    def get_all_trip_data(self,user_id,client_etag,client_version):
        # check etag from cache
        etag_key = f'user{user_id}_trips_version{client_version}'
        cache_etag = self.cache_service.get(etag_key)
        if client_etag == cache_etag:
            return None, client_etag
        
       
        db_version = self.trip_database_service.get_trips_version(user_id=user_id)
        # if in the same version but doesnt have etag
        if client_version == db_version:
            new_etag = self.etag_service.generate_etag(key=etag_key)
            return None, new_etag
        
        
        new_etag_key =f'user{user_id}_trips_version{db_version}'
        new_etag = self.etag_service.generate_etag(key=new_etag_key)
        self.cache_service.set(new_etag_key,new_etag)
        
        trip_data_row = self.database_service.find_item_in_sql('tripin_trips.trips_table','user_id',user_id,return_option='fetchall')
        trip_data_list= []
        for row in trip_data_row:
            default_time =row['created_time']
            row['created_time'] = int(default_time.timestamp()*1000)
            default_time_end =row['ended_time']
            if default_time_end:
                row['ended_time'] = int(default_time_end.timestamp()*1000)
            
            default_image_path = row['image']
            if default_image_path:
                row['image']= self.s3_service.generate_temp_uri(default_image_path)
            
            trip_data_list.append(dict(row))

        # print(trip_data_list)
        return ({'version':db_version,'trip_data_list':trip_data_list if len(trip_data_list)>=1 else None},new_etag)

