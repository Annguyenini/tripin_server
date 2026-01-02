from src.server_config.service.Etag.Etag import EtagService
class UserDataETag (EtagService):
    _instance = None
    _init = False
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls=cls)
        return cls._instance
    
    def __init__(self):
        if self._init:return
        super()
        self._init = True
        
    def get_userdata_etag_handler(self,user_id,user_data):
        key = f'user{user_id}_etag'
        Etag = self.generate_Etag_from_object(user_data)
        self.cacheService.set(key,Etag)
        return Etag
        
        
    def veify_userdata_etag(self,user_id,etag:str):
        key = f'user{user_id}_etag'
        stored_etag = self.get_stored_user_data_etag(key,user_id=user_id)
        return etag == stored_etag
        
    def get_stored_user_data_etag(self,key:str,user_id:int = None, user_name:str = None):
        stored_etag= None
        stored_etag = self.cacheService.get(key=key)
        if stored_etag is None: 
            if user_id:
                userdata = self.databaseService.find_item_in_sql(table='tripin_auth.userdata',item='id',value=user_id)
                stored_etag = userdata['etag']
            elif user_name:
                userdata = self.databaseService.find_item_in_sql(table='tripin_auth.userdata',item='user_name',value=user_name)
                stored_etag = userdata['etag']  
        return stored_etag