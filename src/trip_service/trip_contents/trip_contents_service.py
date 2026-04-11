from src.token.tokenservice import TokenService
from src.database.database import Database
from src.database.s3.s3_service import S3Sevice
from src.database.database_keys import DATABASEKEYS
from src.error_code.error_code import ERROR_KEYS,ERROR_MESSAGE
from src.database.trip_db_service import TripDatabaseService
from src.error_handler.error_handler import ErrorHandler

import hashlib
import psycopg2
from datetime import datetime
import json
from src.server_config.service.cache import Cache
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
            self.cache_service = Cache()
    
           
    def insert_coordinates_to_db(self,trip_id,coordinates):
        """take in the coordinates object and start batching into db

        Args:
            trip_id (): unique trip_id been generate from server
            coordinates (object): object include data from coordinate

        Returns:
            boolean: True if insert successfully / False if failed 
        """
        batch =[]
        con,cur = self.database_service.connect_db()
        # insert into db
        
        

        try:
            query = f'''INSERT INTO tripin_trips.trip_coordinates (
                {DATABASEKEYS.TRIP_COORDINATES.TRIP_ID},
                {DATABASEKEYS.TRIP_COORDINATES.BATCH_VERSION},
                {DATABASEKEYS.TRIP_COORDINATES.TIME_STAMP},
                {DATABASEKEYS.TRIP_COORDINATES.ALTITUDE},
                {DATABASEKEYS.TRIP_COORDINATES.LATITUDE},
                {DATABASEKEYS.TRIP_COORDINATES.LONGITUDE},
                {DATABASEKEYS.TRIP_COORDINATES.HEADING},
                {DATABASEKEYS.TRIP_COORDINATES.SPEED},
                {DATABASEKEYS.TRIP_COORDINATES.COORDINATE_ID},
                {DATABASEKEYS.TRIP_COORDINATES.EVENT},
                {DATABASEKEYS.TRIP_COORDINATES.MODIFIED_TIME}) 
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
            for cor in coordinates:
                # print(cor)
                # print(cor['time_stamp'])
                # time_s = cor['time_stamp']/1000
                # dt = datetime.fromtimestamp(time_s)
                # formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
                batch.append([trip_id,
                              0,
                              cor['time_stamp'],
                              cor["coordinates"]["altitude"],
                              cor["coordinates"]["latitude"],
                              cor["coordinates"]['longitude'], 
                              cor["coordinates"]['heading'], 
                              cor["coordinates"]['speed'],
                              cor["coordinates"]["coordinate_id"],
                              cor["coordinates"]["event"],
                              cor["time_stamp"]
                              ],)
            cur.executemany(query,batch)  
            con.commit()
          
            batch.clear()
        except psycopg2.Error as e:
            return False, None
        print('pass1')

        try:
            self.database_service.close_db(conn=con)
        except Exception as e:
            print("fail to update version",e)
            return False, None
        
        return True, None
        
    def upload_trip_image(self,trip_id:int ,image_path:str):
        status = self.database_service.update_db('tripin_trips.trips_table','id',trip_id,'image',image_path)
        return status
    
    def upload_media(self,type:str,path:str,media,trip_id:int,coordinate_data:object) -> bool | int:
        # current_version = self.trip_database_service.get_trip_contents_version(trip_id=trip_id,version_type=DATABASEKEYS.TRIPS.TRIPS_MEDIAS_VERSION)
        # print(client_version,type(client_version))
        # print(current_version+1,type(current_version))
        # print(client_version,current_version)
        # if client_version != current_version +1:
        #     return False, current_version +1
        longitude = coordinate_data.get('longitude')
        latitude = coordinate_data.get('latitude')
        time = coordinate_data.get('time_stamp')  
        media_id = coordinate_data.get('media_id')  
        coordinate_id =coordinate_data.get('coordinate_id')
        # insert into database (postgres)
        insert_into_db = self.trip_database_service.insert_media_into_db(type=type,media_path=path,longitude=longitude,latitude=latitude,trip_id=trip_id,time=time,modified_time=time,media_id=media_id,coordinate_id=coordinate_id)
        if not insert_into_db:
            return False,None
        
        # upload into cloud (s3)
        insert_into_s3 = self.s3_service.upload_media(f'trips/{trip_id}/{path}',media)
        
        
        if not insert_into_s3:
            self.database_service.delete_from_table('tripin_trips.trip_medias','trip_id',trip_id,True,'key',path)
            return False,None
        # update media version of trip 
        
        # await self.trip_database_service.update_trip_version(DATABASEKEYS.TRIPS.TRIPS_MEDIAS_VERSION,trip_id=trip_id,version=client_version)
        hash = self.trip_database_service.generate_trip_media_hash(trip_id=trip_id)
        return True,hash
    
    def delete_media(self,media_id:str,trip_id:int,modified_time:int) -> bool | str:
        # remove from db,
        # get old data from database
        media_data = None
        try:
            con,cur = self.database_service.connect_db()
            cur.execute(f'''
            UPDATE {DATABASEKEYS.TABLES.TRIP_MEDIAS} 
            SET {DATABASEKEYS.TRIP_MEDIAS.EVENT} = %s,
                {DATABASEKEYS.TRIP_MEDIAS.MODIFIED_TIME} = %s     
            WHERE {DATABASEKEYS.TRIP_MEDIAS.MEDIA_ID} =%s
            RETURNING *
            ''',('remove',modified_time,media_id))
            media_data = cur.fetchone()
            con.commit()
            self.database_service.close_db(conn=con)
        except Exception as e:
            ErrorHandler().logger('trip_content').error('Failed to update delete media',e)
            return False,{'code':'failed_database'}
   
        if not media_data:
            return False,{'code':'media_not_exist'}

        media_path = media_data['media_path']        
        s3_path = f'trips/{trip_id}/{media_path}'
        # remove form s3
        remove_from_s3 = self.s3_service.delete_media(path=s3_path)
        if not remove_from_s3:     
           return False,{'code':'failed_cloud'}
         
        return True,None
       
    def delete_trip_coord(self,coordinate_id:str,modified_time):
        con,cur =None,None
        try:
            con,cur = self.database_service.connect_db()
            cur.execute(f'''
            UPDATE {DATABASEKEYS.TABLES.TRIP_COORDINATES} 
            SET {DATABASEKEYS.TRIP_COORDINATES.EVENT} = %s,
                {DATABASEKEYS.TRIP_COORDINATES.MODIFIED_TIME} = %s     
            WHERE {DATABASEKEYS.TRIP_COORDINATES.COORDINATE_ID} =%s
            ''',('remove',modified_time,coordinate_id,))
            con.commit()
            return True,None
        except Exception as e:
            ErrorHandler().logger('trip_content').error('Failed to update delete media',e)
            return False,{'code':'failed_database'}
        finally:
            self.database_service.close_db(conn=con)

    def get_trip_coors(self , trip_id:int):
        # return a list of rowdict from the client version up to current version
        try:
            coors = self.trip_database_service.get_trip_coordinates(trip_id=trip_id)
            return [dict(r) for r in coors] if coors else None, 0

        except Exception as e:
            print ('Error at getting coordinates ',e)
            return None, None
    def get_trip_belong_to(self,trip_id:int)->int:
        user_id = self.trip_database_service.get_user_id_from_trip_id(trip_id=trip_id)
        return user_id
    def get_trip_media(self,trip_id:int):
      
        # server_version = self.trip_database_service.get_trip_contents_version(trip_id=trip_id,version_type=DATABASEKEYS.TRIPS.TRIPS_MEDIAS_VERSION)
        # # print('media versions ', client_version,server_version)
        # if client_version :
        #     if int(client_version) == server_version:
        #         return None,None
        try:
            medias = self.database_service.find_item_in_sql('tripin_trips.trip_medias','trip_id',trip_id,return_option='fetchall')
            for i in range( len(medias)):
                default_key = medias[i]['media_path']
                print(default_key)
                medias[i]['media_path'] = self.s3_service.generate_temp_uri(f'trips/{trip_id}/'+default_key)
                medias[i]=dict(medias[i])
            # print(medias)
            return medias
        except Exception as e:
            ErrorHandler().logger('trip_content').error('failed to get trip media',e)
            return None
            
    def get_trip_media_metadata(self,trip_id:int):
        """_summary_

        Args:
            trip_id (int): _description_
        """
        medias = self.database_service.find_item_in_sql('tripin_trips.trip_medias','trip_id',trip_id,return_option='fetchall')
        return [dict(media) for media in medias]
