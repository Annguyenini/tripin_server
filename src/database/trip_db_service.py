from src.database.database import Database
from datetime import datetime
class TripDatabaseService (Database):
    _instance = None
    _init = False
    def __new__(cls):
        if cls._instance is None :
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._init:
            return  
        super()
        self._init = True

    def insert_to_database_trip(self,user_id:int,trip_name:str,imageUri:str):
        """insert new row in to database trip table / return 2 value

        Args:
            user_id (int): _userid_
            trip_name (str): _tripname_

        Returns:
            _bool, int_: _status, trip_id_
        """
        con,cur = self.connect_db()
        created_time = datetime.now()
        cur.execute(f'INSERT INTO tripin_trips.trips_table (user_id,trip_name,created_time, active,image) VALUES (%s,%s,%s,%s,%s) RETURNING id',(user_id,trip_name,created_time,True,imageUri))
        trip_id = cur.fetchone()['id']
        con.commit()
        con.close()
        if cur.rowcount >=1:
            print("insert successfully")
            return True, trip_id
        return False,0 
    
    def insert_media_into_db(self, type:str,key:str,longitude:float,latitude:float,trip_id:int,time):
        con,cur = self.connect_db()
        cur.execute(f'INSERT INTO tripin_trips.trip_medias (media_type,key,longitude,latitude,trip_id,time_stamp) VALUES (%s,%s,%s,%s,%s,%s)',(type,key,longitude,latitude,trip_id,time))
        con.commit()
        if cur.rowcount >=1:
            return True
        else: return False
        
    def update_trips_version(self,user_id):
        con,cur =self.connect_db()
        cur.execute(f'UPDATE tripin_auth.userdata SET trip_version = trip_version+1 WHERE id = %s',(user_id))
        con.commit()
        con.close()
        if cur.rowcount <=0:
            return False
        return True
    
    def get_trips_version(self,user_id):
        con,cur =self.connect_db()
        cur.execute(f'SELECT trip_version FROM tripin_auth.userdata WHERE id = %s',(user_id))
        version = cur.fetchone()
        return version