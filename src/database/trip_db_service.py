from src.database.database import Database
from datetime import datetime
from src.database.database_keys import DATABASEKEYS
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
        super().__init__()
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
        cur.execute(f'INSERT INTO {DATABASEKEYS.TABLES.TRIPS} (user_id,trip_name,created_time, active,image) VALUES (%s,%s,%s,%s,%s) RETURNING id',(user_id,trip_name,created_time,True,imageUri))
        trip_id = cur.fetchone()['id']
        con.commit()
        con.close()
        if cur.rowcount >=1:
            print("insert successfully")
            return True, trip_id
        return False,0 
    
    def insert_media_into_db(self, type:str,key:str,longitude:float,latitude:float,trip_id:int,time):
        con,cur = self.connect_db()
        cur.execute(f'INSERT INTO {DATABASEKEYS.TABLES.TRIP_MEDIAS} (media_type,key,longitude,latitude,trip_id,time_stamp) VALUES (%s,%s,%s,%s,%s,%s)',(type,key,longitude,latitude,trip_id,time))
        con.commit()
        if cur.rowcount >=1:
            return True
        else: return False
        
    def update_all_trips_version(self,user_id):
        con,cur =self.connect_db()
        cur.execute(f'UPDATE {DATABASEKEYS.TABLES.USERDATA} SET trips_data_version = trips_data_version+1 WHERE id = %s',(user_id,))
        con.commit()
        con.close()
        return True if cur.rowcount>=1 else False
    
    def update_trip_version (self,type_of_version:str,trip_id:int):
        allow_type = ['']
        con,cur = self.connect_db()
        cur.execute(f'UPDATE {DATABASEKEYS.TABLES.TRIPS} SET {type_of_version} = {type_of_version}+1 WHERE id = %s',(trip_id))
        con.commit()
        return True if cur.rowcount>=1 else False
        
    
    def get_user_trips_data(self,user_id:int,data_type:str) -> any:
        con,cur =self.connect_db()
        cur.execute(f'SELECT {data_type} FROM {DATABASEKEYS.TABLES.USERDATA} WHERE id = %s',(user_id,))
        con.commit()
        version = cur.fetchone()
        return version[0] if version else None
    