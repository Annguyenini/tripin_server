from src.database.database import Database

class UserService:
    _instace = None
    def __new__(cls):
        if cls._instace:return cls._instace
        cls._instace = super().__new__(cls)
        
    def __init__(self):
        self.databaseService = Database()
    
    def get_user_data_from_database(self,username):
         ##find username in database
        userdata_row = self.databaseService.find_item_in_sql(table="tripin_auth.userdata",item="user_name",value=username)
        ##return false if username not exist
        if userdata_row is None:
            return None
        
        userid=userdata_row["id"] 
        display_name=userdata_row["display_name"] 
        username=userdata_row["user_name"] 
        role = userdata_row["role"]
        avatar = userdata_row['avatar']
        data = {'user_id':userid,'display_name':display_name,'user_name':username,'role':role,'avatar':avatar}
        return  data
        