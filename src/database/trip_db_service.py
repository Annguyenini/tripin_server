from src.database.database import Database
from datetime import datetime
from src.database.database_keys import DATABASEKEYS
from src.error_handler.error_handler import ErrorHandler
import logging
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
        self.ErrorHandler = ErrorHandler()
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
        try:
            cur.execute(f'INSERT INTO {DATABASEKEYS.TABLES.TRIPS} (user_id,trip_name,created_time, active,image) VALUES (%s,%s,%s,%s,%s) RETURNING id',(user_id,trip_name,created_time,True,imageUri))
            trip_id = cur.fetchone()['id']
            con.commit()
            self.close_db(conn=con)
            if cur.rowcount >=1:
                print("insert successfully")
                return True, trip_id
        except Exception as e:
            self.ErrorHandler.logger('TripDataBase').error('Failed to insert to database',body=e)
            return False,0 
    
    def insert_media_into_db(self, type:str,media_path:str,longitude:float,latitude:float,trip_id:int,time:int,modified_time:int,media_id:str,coordinate_id:str) -> bool:
        """insert in to trip medias table

        Args:
            type (str): _description_
            media_path (str): _description_
            longitude (float): _description_
            latitude (float): _description_
            trip_id (int): _description_
            time (int): _description_
            image_id (str): _description_

        Returns:
            bool: _description_
        """
        try:
            con,cur = self.connect_db()
            cur.execute(f'''INSERT INTO {DATABASEKEYS.TABLES.TRIP_MEDIAS} (
                {DATABASEKEYS.TRIP_MEDIAS.MEDIA_TYPE}, 
                {DATABASEKEYS.TRIP_MEDIAS.MEDIA_PATH}, 
                {DATABASEKEYS.TRIP_MEDIAS.LONGITUDE}, 
                {DATABASEKEYS.TRIP_MEDIAS.LATITUDE}, 
                {DATABASEKEYS.TRIP_MEDIAS.TRIP_ID}, 
                {DATABASEKEYS.TRIP_MEDIAS.TIME_STAMP},
                {DATABASEKEYS.TRIP_MEDIAS.MODIFIED_TIME},
                {DATABASEKEYS.TRIP_MEDIAS.MEDIA_ID},
                {DATABASEKEYS.TRIP_MEDIAS.COORDINATE_ID}) 
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                (type,media_path,longitude,latitude,trip_id,time,modified_time,media_id,coordinate_id))
            con.commit()
            self.close_db(conn=con)
            if cur.rowcount >=1:
                return True
            else: return False
        except Exception as e:
            self.ErrorHandler.logger('TripDatabase').error('Failed to insert Media into database',body=e)

    def update_all_trips_version(self,user_id):
        try:
            con,cur =self.connect_db()
            cur.execute(f'UPDATE {DATABASEKEYS.TABLES.USERDATA} SET trips_data_version = trips_data_version+1 WHERE id = %s',(user_id,))
            con.commit()
            self.close_db(conn=con)
            return True if cur.rowcount>=1 else False
        except Exception as e:
            self.ErrorHandler.logger('TripDataBase').error('Failed at update all trips version',body=e)
            return False
    def update_trip_version (self,type_of_version:str,trip_id:int,version:int = None):
        allow_type = ['']
        try:
            con,cur = self.connect_db()
            cur.execute(f'UPDATE {DATABASEKEYS.TABLES.TRIPS} SET {type_of_version} = {type_of_version}+1 WHERE id = %s',(trip_id,))
            con.commit()
            self.close_db(conn=con)
            return True if cur.rowcount>=1 else False
        except Exception as e:
            self.ErrorHandler.logger('TripDataBase').error('Failed to update trip version',body=e)
            return False
    
    def get_user_trips_data(self,user_id:int,data_type:str) -> any:
        try:    
            con,cur =self.connect_db()
            cur.execute(f'SELECT {data_type} FROM {DATABASEKEYS.TABLES.USERDATA} WHERE id = %s',(user_id,))
            con.commit()
            self.close_db(conn=con)
            version = cur.fetchone()
            return version[0] if version else None
        except Exception as e:
            self.ErrorHandler.logger('TripDataBase').error('Failed at get user trips data',body=e)
            return False

    def get_trip_contents_version(self,trip_id:int,version_type:str) ->int:
        try:  
            con,cur = self.connect_db()
            cur.execute(f'SELECT {version_type} FROM {DATABASEKEYS.TABLES.TRIPS} WHERE {DATABASEKEYS.TRIPS.TRIP_ID} = %s',(trip_id,))
            con.commit()
            version = cur.fetchone()
            return version[0] if version else None
        except Exception as e:
            self.ErrorHandler.logger('TripDataBase').error('Failed to get trip content version',body=e)
            return False
        finally:
            self.close_db(conn=con)

    def get_user_id_from_trip_id(self,trip_id:int)->int:
        try:
            con,cur = self.connect_db()
            cur.execute(f'SELECT {DATABASEKEYS.TRIPS.USER_ID} FROM {DATABASEKEYS.TABLES.TRIPS} WHERE {DATABASEKEYS.TRIPS.TRIP_ID} = %s',(trip_id,))
            con.commit()
            return cur.fetchone()[0]
        except Exception as e:
            self.ErrorHandler.logger('TripDataBase').error('Failed to get user id from trip id',body=e)
            return False
        finally:
            self.close_db(conn=con)

    def get_trip_coordinates (self,trip_id:int):
        # print(trip_id,client_version)
        con,cur = None,None

        try:
            con,cur = self.connect_db()

            cur.execute(f'''SELECT * FROM {DATABASEKEYS.TABLES.TRIP_COORDINATES} 
                        WHERE {DATABASEKEYS.TRIP_COORDINATES.TRIP_ID} = %s 
                        ORDER BY {DATABASEKEYS.TRIP_COORDINATES.COORDINATES_ID} ASC''',(trip_id,))
            con.commit()
            coors = cur.fetchall()
            # print(coors)
            return coors if coors else None
        except Exception as e:
            self.ErrorHandler.logger('TripDataBase').error('Failed to get trip coordinate',body=e)
            return False
        finally:
            if con :self.close_db(conn=con)

    def trip_owner_validation(self,user_id:int,trip_id:int)->bool:
        try:
            result = self.find_item_in_sql(DATABASEKEYS.TABLES.TRIPS,
                                DATABASEKEYS.TRIPS.TRIP_ID,
                                trip_id,
                                True,
                                DATABASEKEYS.TRIPS.USER_ID,
                                user_id)
            return True if result else False
        except Exception as e:
            self.ErrorHandler.logger('TripDataBase').error('Failed to validate trip owner',body=e)
            return False

    def get_trip_data_by_shared_token(self,token:str):
        try:
            con,cur = self.connect_db()
            cur.execute(f'''SELECT 
                        {DATABASEKEYS.TABLES.TRIP_SHARED_LINKS}.*,
                        {DATABASEKEYS.TABLES.TRIPS}.*,
                        {DATABASEKEYS.TABLES.USERDATA}.display_name
                        FROM {DATABASEKEYS.TABLES.TRIP_SHARED_LINKS}
                        INNER JOIN {DATABASEKEYS.TABLES.TRIPS}
                        ON {DATABASEKEYS.TRIP_SHARED_LINKS.TRIP_ID} = {DATABASEKEYS.TABLES.TRIPS}.id
                        INNER JOIN {DATABASEKEYS.TABLES.USERDATA}
                        ON {DATABASEKEYS.TABLES.TRIPS}.user_id = {DATABASEKEYS.TABLES.USERDATA}.id
                        WHERE {DATABASEKEYS.TRIP_SHARED_LINKS.TOKEN} = %s''', (token,))
            
            row = cur.fetchone()
            con.commit()
            self.close_db(conn=con)
            return row if row else None
        except Exception as e:
            self.ErrorHandler.logger('TripDataBase').error('Failed to update trip version',body=e)
            return False

    def get_trip_media_metadatas(self,trip_id:int):
        """return all the metadatas for the trip 
        include image_id, modified_time

        Args:
            trip_id (int): _description_

        Returns:
            _type_: _description_
        """
        try:
            con,cur = self.connect_db()
            cur.execute(f'''
                        SELECT {DATABASEKEYS.TRIP_MEDIAS.MEDIA_ID} ,{DATABASEKEYS.TRIP_MEDIAS.EVENT},
                        {DATABASEKEYS.TRIP_MEDIAS.MODIFIED_TIME}
                        FROM {DATABASEKEYS.TABLES.TRIP_MEDIAS}
                        WHERE {DATABASEKEYS.TRIP_MEDIAS.TRIP_ID} = %s
                        ''' ,(trip_id,))
            row = cur.fetchall()
            con.commit()
            self.close_db(conn=con)
            return row if row else None
        except Exception as e:
            self.ErrorHandler.logger('TripDataBase').error('Failed to get trip metadata',body=e)
            return False

    def generate_trip_media_hash(self,trip_id:int):
        con,cur = None,None
        try:
            con,cur = self.connect_db()
            cur.execute(f'''
                        SELECT COUNT(*), MAX({DATABASEKEYS.TRIP_MEDIAS.MODIFIED_TIME})
                        FROM {DATABASEKEYS.TABLES.TRIP_MEDIAS}
                        WHERE {DATABASEKEYS.TRIP_MEDIAS.TRIP_ID} = %s
                        ''' ,(trip_id,))
            count,max = cur.fetchone()
            con.commit()
            return f'{count}:{max}' 
        except Exception as e:
            self.ErrorHandler.logger('TripDataBase').error('Failed to get trip meida max',body=e)
            return None
        finally:
            if con: self.close_db(conn=con)

    def generate_trip_coordinate_hash(self,trip_id:int):
        con,cur = None,None

        try:
            con,cur = self.connect_db()
            cur.execute(f'''
                        SELECT COUNT(*) , MAX({DATABASEKEYS.TRIP_COORDINATES.MODIFIED_TIME})
                        FROM {DATABASEKEYS.TABLES.TRIP_COORDINATES}
                        WHERE {DATABASEKEYS.TRIP_COORDINATES.TRIP_ID} = %s
                        ''' ,(trip_id,))
            count , max = cur.fetchone()
            con.commit()
            print(count,max)
            return f'{count}:{max}'
        except Exception as e:
            self.ErrorHandler.logger('TripDataBase').error('Failed to get trip coordinate max',body=e)
            return None
        finally:
            if con :self.close_db(conn=con)

    