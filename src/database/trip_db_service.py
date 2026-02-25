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
    
    def insert_media_into_db(self, type:str,media_path:str,longitude:float,latitude:float,trip_id:int,version:int,time) -> bool:
        con,cur = self.connect_db()
        cur.execute(f'INSERT INTO {DATABASEKEYS.TABLES.TRIP_MEDIAS} (media_type,media_path,longitude,latitude,trip_id,version,time_stamp) VALUES (%s,%s,%s,%s,%s,%s,%s)',(type,media_path,longitude,latitude,trip_id,version,time))
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
    
    def update_trip_version (self,type_of_version:str,trip_id:int,version:int = None):
        allow_type = ['']
        con,cur = self.connect_db()
        cur.execute(f'UPDATE {DATABASEKEYS.TABLES.TRIPS} SET {type_of_version} = {type_of_version}+1 WHERE id = %s',(trip_id,))
        con.commit()
        return True if cur.rowcount>=1 else False
        
    
    def get_user_trips_data(self,user_id:int,data_type:str) -> any:
        con,cur =self.connect_db()
        cur.execute(f'SELECT {data_type} FROM {DATABASEKEYS.TABLES.USERDATA} WHERE id = %s',(user_id,))
        con.commit()
        version = cur.fetchone()
        return version[0] if version else None
    
    def get_trip_contents_version(self,trip_id:int,version_type:str) ->int:
        con,cur = self.connect_db()
        cur.execute(f'SELECT {version_type} FROM {DATABASEKEYS.TABLES.TRIPS} WHERE {DATABASEKEYS.TRIPS.TRIP_ID} = %s',(trip_id,))
        con.commit()
        version = cur.fetchone()
        return version[0] if version else None
    def get_user_id_from_trip_id(self,trip_id:int)->int:
        con,cur = self.connect_db()
        cur.execute(f'SELECT {DATABASEKEYS.TRIPS.USER_ID} FROM {DATABASEKEYS.TABLES.TRIPS} WHERE {DATABASEKEYS.TRIPS.TRIP_ID} = %s',(trip_id,))
        con.commit()
        return cur.fetchone()[0]
    
    def get_trip_coordinates (self,trip_id:int,client_version:int = 0):
        if not client_version: client_version =0
        print(trip_id,client_version)
        try:
            con,cur = self.connect_db()
            cur.execute(f'''SELECT * FROM {DATABASEKEYS.TABLES.TRIP_COORDINATES} 
                        WHERE {DATABASEKEYS.TRIP_COORDINATES.TRIP_ID} = %s 
                        AND {DATABASEKEYS.TRIP_COORDINATES.BATCH_VERSION} > %s 
                        ORDER BY {DATABASEKEYS.TRIP_COORDINATES.COORDINATES_ID} ASC''',(trip_id,client_version,))
            con.commit()
            coors = cur.fetchall()
            con.close()
            print(coors)
            return coors if coors else None
        except Exception as e:
            print('Error at getting coordinates ',e)
    
    def trip_owner_validation(self,user_id:int,trip_id:int)->bool:
        result = self.find_item_in_sql(DATABASEKEYS.TABLES.TRIPS,
                              DATABASEKEYS.TRIPS.TRIP_ID,
                              trip_id,
                              True,
                              DATABASEKEYS.TRIPS.USER_ID,
                              user_id)
        return True if result else False