from src.token.tokenservice import TokenService
from src.database.database import Database
from src.database.s3.s3_service import S3Sevice
from src.database.s3.s3_dirs import TRIP_DIR
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
            self.s3_service = S3Sevice()
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
        create_trip,trip_id = self.database_service.insert_to_database_trip(user_id = user_id, trip_name = trip_name,imageUri=imageUri)
        if create_trip:
            return True, f"Created trip {trip_name} successfully", trip_id
        else: 
            return False, "Error occur while creating trip.",None
           
           
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
            query = "INSERT INTO tripin_trips.trip_coordinates (trip_id,time_stamp,altitude,latitude,longitude,heading,speed) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            for cor in coordinates:
                time_s = cor['time_stamp']/1000
                dt = datetime.fromtimestamp(time_s)
                formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
                batch.append([trip_id,formatted,cor["coordinates"]["altitude"],cor["coordinates"]["latitude"],cor["coordinates"]['longitude'], cor["coordinates"]['heading'], cor["coordinates"]['speed']])
            cur.executemany(query,batch)
            batch.clear()
        except psycopg2.Error as e:
            print("fail to insert into database",e)
            return False
        con.commit()
        cur.close()
        con.close()
        return True
        
          
    def end_a_trip(self, trip_id:int):
        print(trip_id)
        update_trip_status = self.database_service.update_db(table = "tripin_trips.trips_table", item = "id", value= trip_id, item_to_update = "active",value_to_update = False)
        if not update_trip_status:
            return False, f"Error while trying to end trip {trip_id}"
        update_trip_ended_time = self.database_service.update_db(table = "tripin_trips.trips_table", item="id", value= trip_id ,item_to_update="ended_time",value_to_update=datetime.now())
        if not update_trip_ended_time:
            return False, f"Error while trying to end trip {trip_id}"
        return True,f"Successfully end trip {trip_id}" 
    
    def get_trip_data(self,user_id):
        trip_data_row = self.database_service.find_item_in_sql('tripin_trips.trips_table','user_id',user_id,True,'active',True)
        if trip_data_row is None :
            return None
        trip_id = trip_data_row['id']
        trip_name = trip_data_row['trip_name']
        created_timestamp = trip_data_row['created_time']
        created_time = int(created_timestamp.timestamp() * 1000)
        trip_image_default = trip_data_row['image']
        
        trip_image = None
        if trip_image_default:
            trip_image = self.s3_service.generate_image_uri(trip_image_default)
            
        trip_data = None 
        if trip_data_row:
            trip_data = {'trip_id':trip_id,'trip_name':trip_name,'created_time':created_time,'trip_image':trip_image if trip_image else None}
        return trip_data
    
    def get_all_trip_data(self,user_id):
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
                row['image']= self.s3_service.generate_image_uri(default_image_path)
            
            trip_data_list.append(dict(row))

        # print(trip_data_list)
        return trip_data_list if len(trip_data_list)>=1 else None


    def upload_trip_image(self,trip_id:int ,image_path:str):
        status = self.database_service.update_db('tripin_trips.trips_table','id',trip_id,'image',image_path)
        return status