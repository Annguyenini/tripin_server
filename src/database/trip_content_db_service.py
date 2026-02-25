from src.database.database import Database
from src.database.trip_db_service import TripDatabaseService
from src.database.database_keys import DATABASEKEYS
class TripContentsDatabaseService (TripDatabaseService):
    _instance = None 
    _init = False
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        
        
   