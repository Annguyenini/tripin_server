from src.database.database import Database
from src.database.database_keys import DATABASEKEYS
class TripContentsDatabaseService (Database):
    _instance = None 
    _init = False
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        
        
    def trip_owner_validation(self,user_id:int,trip_id:int)->bool:
        result = self.find_item_in_sql(DATABASEKEYS.TABLES.TRIPS,
                              DATABASEKEYS.TRIPS.TRIP_ID,
                              trip_id,
                              True,
                              DATABASEKEYS.TRIPS.USER_ID,
                              user_id)
        return True if result else False