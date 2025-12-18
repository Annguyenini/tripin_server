from src.token.tokenservice import TokenService
from src.database.database import Database
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
            self._init =True
    def get_active_trip(self,user_id):
        self.database_service.find_item_in_sql(table="tripin_trips.trip_table", )
    
    def process_new_trip(self,user_id,trip_name):
        # trip_db layout 
        # trip_id | trip_name | user_id | start_time | end_time | active

        ##return if user are currently in another aactive 
        exist_trip = self.database_service.find_item_in_sql(table="tripin_trips.trips_table",item="user_id",value=user_id,
                                                            second_condition=True,second_item="active",second_value=True )

        if exist_trip is not None:
            return False, f"Currently in {exist_trip[1]}"
    
        ##return if exists trip name from user
        exist_trip_name = self.database_service.find_item_in_sql(table = "tripin_trips.trips_table", item = "trip_name", value = trip_name,second_condition=True, second_item="user_id",second_value=user_id)
        
        if exist_trip_name is not None:
            return False, f"Trip name: {trip_name} already exist!"
        
        ##process to create new trip
        create_trip,trip_id = self.database_service.insert_to_database_trip(user_id = user_id, trip_name = trip_name)
        if create_trip >=1 :
            return True, f"Created trip {trip_name} successfully", trip_id
        else: 
            return False, "Error occur while creating trip." 
           
    def end_a_trip(self, trip_id):
        end_trip = self.database_service.update_db(table = "tripin_trips.trip_table", item = "id", value= trip_id, item_to_update = "active",value_to_update = False)
        if not end_trip:
            return False, f"Error while trying to end trip {trip_id}"
        return True,f"Successfully end trip {trip_id}" 
    
    