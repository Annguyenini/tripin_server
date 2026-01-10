from src.token.tokenservice import TokenService
from src.database.database import Database
from src.database.s3.s3_service import S3Sevice
from src.database.database_keys import DATABASEKEYS
from src.database.trip_db_service import TripDatabaseService
import psycopg2
from datetime import datetime
import json
class TripContentService:
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
            self._init =True
    
           
    def insert_coordinates_to_db(self,trip_id,client_version,coordinates):
        """take in the coordinates object and start batching into db

        Args:
            trip_id (): unique trip_id been generate from server
            coordinates (object): object include data from coordinate

        Returns:
            boolean: True if insert successfully / False if failed 
        """
        # get current version 
        current_batch_version = self.trip_database_service.get_trip_contents_version(trip_id=trip_id,version_type=DATABASEKEYS.TRIPS.TRIP_COORDINATES_VERSION)
        # if new data version != to next batch version return false with the request batch version
        if not client_version:
            client_version = current_batch_version
             
        if client_version < current_batch_version +1:
                return False, current_batch_version  
        batch =[]
        con,cur = self.database_service.connect_db()
        # insert into db
        
        
        try:
            query = "INSERT INTO tripin_trips.trip_coordinates (trip_id,batch_version,time_stamp,altitude,latitude,longitude,heading,speed) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            for cor in coordinates:
                print(cor['time_stamp'])
                time_s = cor['time_stamp']/1000
                dt = datetime.fromtimestamp(time_s)
                formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
                batch.append([trip_id,current_batch_version+1,formatted,cor["coordinates"]["altitude"],cor["coordinates"]["latitude"],cor["coordinates"]['longitude'], cor["coordinates"]['heading'], cor["coordinates"]['speed']])
            cur.executemany(query,batch)            
            batch.clear()
        except psycopg2.Error as e:
            print("fail to insert into database",e)
            return False
        
        self.trip_database_service.update_trip_version(type_of_version=DATABASEKEYS.TRIPS.TRIP_COORDINATES_VERSION,trip_id=trip_id)
        con.commit()
        cur.close()
        con.close()
        
        
        return True, None
        
    def upload_trip_image(self,trip_id:int ,image_path:str):
        status = self.database_service.update_db('tripin_trips.trips_table','id',trip_id,'image',image_path)
        return status
    
    def upload_media(self,type:str,path:str,media,longitude:float,latitude:float,trip_id:int,time):
        insert_into_db = self.trip_database_service.insert_media_into_db(type=type,key=path,longitude=longitude,latitude=latitude,trip_id=trip_id,time=time)
        if not insert_into_db:
            return False
        
        insert_into_s3 = self.s3_service.upload_media(f'trips/{trip_id}/{path}',media)
        if not insert_into_s3:
            self.database_service.delete_from_table('tripin_trips.trip_medias','trip_id',trip_id,True,'key',path)
            return False
        return True
    
    
    def get_trip_coors(self,client_version:int , trip_id:int):
        # return a list of rowdict from the client version up to current version
        coors = self.trip_database_service.get_trip_coordinates(trip_id=trip_id,client_version=client_version)
        return [dict(r) for r in coors]
    
    def get_trip_media(self,trip_id:int):
        medias = self.database_service.find_item_in_sql('tripin_trips.trip_medias','trip_id',trip_id,return_option='fetchall')
        for i in range( len(medias)):
            default_key = medias[i]['key']
            print(default_key)
            medias[i]['key'] = self.s3_service.generate_temp_uri(f'trips/{trip_id}/'+default_key)
            medias[i]=dict(medias[i])
        print(medias)
        return medias
