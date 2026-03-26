from src.token.tokenservice import TokenService
from src.database.database import Database
from src.database.s3.s3_service import S3Sevice
from src.database.database_keys import DATABASEKEYS
from src.database.trip_db_service import TripDatabaseService
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
        # print(client_version,current_batch_version+1)
        print(current_batch_version,coordinates)
        if client_version != current_batch_version +1:
            # print(current_batch_version,type(current_batch_version))
            # print(client_version,type(client_version))

            return False, current_batch_version
        batch =[]
        con,cur = self.database_service.connect_db()
        # insert into db
        
        print('pass')

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
                {DATABASEKEYS.TRIP_COORDINATES.EVENT}) 
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
            for cor in coordinates:
                # print(cor)
                # print(cor['time_stamp'])
                # time_s = cor['time_stamp']/1000
                # dt = datetime.fromtimestamp(time_s)
                # formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
                batch.append([trip_id,
                              client_version,
                              cor['time_stamp'],
                              cor["coordinates"]["altitude"],
                              cor["coordinates"]["latitude"],
                              cor["coordinates"]['longitude'], 
                              cor["coordinates"]['heading'], 
                              cor["coordinates"]['speed'],
                              cor["coordinates"]["coordinate_id"],
                              cor["coordinates"]["event"],
                              ],)
            cur.executemany(query,batch)  
            con.commit()
          
            batch.clear()
        except psycopg2.Error as e:
            print("fail to insert into database",e)
            return False, None
        print('pass1')

        try:
            self.trip_database_service.update_trip_version(type_of_version=DATABASEKEYS.TRIPS.TRIP_COORDINATES_VERSION,trip_id=trip_id)
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
        hash = self.get_trip_medias_hash(trip_id=trip_id)
        return True,hash
    
    def delete_media(self,media_id:str,trip_id:int) -> bool | str:
        # remove from db,
        # get old data from database
        old_data = self.trip_database_service.find_item_in_sql(
            table=DATABASEKEYS.TABLES.TRIP_MEDIAS,
            item= DATABASEKEYS.TRIP_MEDIAS.MEDIA_ID,
            value=media_id,
            second_condition=True,
            second_item=DATABASEKEYS.TRIP_MEDIAS.TRIP_ID,
            second_value=trip_id)
        if not old_data:
            return False,{'code':'media_not_exist'}
        media_path = old_data['media_path']
        remove_from_db = self.trip_database_service.delete_from_table(
            table= DATABASEKEYS.TABLES.TRIP_MEDIAS,
            item= DATABASEKEYS.TRIP_MEDIAS.MEDIA_ID,
            value=media_id,
            second_condition= True,
            second_item=DATABASEKEYS.TRIP_MEDIAS.TRIP_ID,
            second_value=trip_id
        )
        print(media_id,trip_id,media_path)
        if not remove_from_db:
            return False,{'code':'failed_database'}
        s3_path = f'trips/{trip_id}/{media_path}'
        # remove form s3
        remove_from_s3 = self.s3_service.delete_media(path=s3_path)
        if not remove_from_s3:
            if not remove_from_db:
                return False,{'code':'failed_cloud'}
         
        return True,None
       
    def get_trip_coors(self,client_version:int , trip_id:int):
        # return a list of rowdict from the client version up to current version
        try:
            server_version = self.trip_database_service.get_trip_contents_version(trip_id=trip_id,version_type=DATABASEKEYS.TRIPS.TRIP_COORDINATES_VERSION)
            if client_version:
                if int(client_version) == server_version:
                    return None,None
            coors = self.trip_database_service.get_trip_coordinates(trip_id=trip_id,client_version=client_version)
            print(client_version,trip_id,coors)

            return [dict(r) for r in coors] if coors else None, server_version

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
        medias = self.database_service.find_item_in_sql('tripin_trips.trip_medias','trip_id',trip_id,return_option='fetchall')
        for i in range( len(medias)):
            default_key = medias[i]['media_path']
            print(default_key)
            medias[i]['media_path'] = self.s3_service.generate_temp_uri(f'trips/{trip_id}/'+default_key)
            medias[i]=dict(medias[i])
        # print(medias)
        return medias

    def get_trip_medias_hash(self,trip_id:int):
        """return a hash for all trip_id

        Args:
            trip_id (int): _description_

        Returns:
            _type_: _description_
        """
        all_trip_data = self.trip_database_service.get_trip_media_metadatas(trip_id=trip_id)
        if not all_trip_data:
            return None
        
        sorted_data =[]
        for row in all_trip_data:
            if row['media_id'] is not None:
                sorted_data.append(row)
        sorted_data.sort(key=lambda row: row['media_id'])
        ids_string = ','.join([str(row['media_id']) for row in sorted_data])
        return hashlib.md5(ids_string.encode()).hexdigest()


    def get_trip_media_metadata(self,trip_id:int):
        """_summary_

        Args:
            trip_id (int): _description_
        """
        medias = self.database_service.find_item_in_sql('tripin_trips.trip_medias','trip_id',trip_id,return_option='fetchall')
        return [dict(media) for media in medias]