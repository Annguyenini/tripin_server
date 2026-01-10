from src.database.database import Database
from src.database.database_keys import DATABASEKEYS
from src.database.s3.s3_service import S3Sevice
from src.server_config.service.Etag.auth_etag_service import AuthEtagService
from src.server_config.service.cache import Cache
class UserService:
    _instace = None
    _init = False
    def __new__(cls):
        if cls._instace:return cls._instace
        cls._instace = super().__new__(cls)
        
    def __init__(self):
        if self._init:
            return 
        
        self.databaseService = Database()
        self.s3Service = S3Sevice()
        self.authEtagService = AuthEtagService()
        self.cacheService = Cache()
        self._init =True
    
    def get_user_data_from_database(self,user_id:int,client_etag:str = None)->object:
         
        # check etag in cache         
        etag_key = self.authEtagService.generate_key(user_id=user_id)
        cache_etag = self.authEtagService.get_userdata_etag_from_cache(key=etag_key)
        if cache_etag:
            if client_etag == cache_etag:
                return(None,cache_etag)
        else:
            # set the etag to cahche
            db_etag = self.authEtagService.get_userdata_etag_from_database(user_id=user_id)
            if db_etag:
                if client_etag == db_etag:
                    self.cacheService.set(key=etag_key,time=3600,data=db_etag)
                    return(None,db_etag)
        
        
         ##find userdata in database
        userdata_row = self.databaseService.find_item_in_sql(table=DATABASEKEYS.TABLES.USERDATA,item=DATABASEKEYS.USERDATA.USER_ID,value=user_id)
        ##return false if username not exist
        if userdata_row is None:
            return None,None
        
        userid=userdata_row["id"] 
        display_name=userdata_row["display_name"] 
        username=userdata_row["user_name"] 
        role = userdata_row["role"]
        avatar = userdata_row['avatar']
        userdata_version = userdata_row['userdata_version']
        if avatar:
            avatar = self.s3Service.generate_temp_uri(key=avatar)
            
            
        etag_key = self.authEtagService.generate_key(user_id=user_id)
        etag_string = self.authEtagService.genarate_etag_string(user_id=user_id,version= userdata_version)
        etag = self.authEtagService.generate_etag(key=etag_string)
        
        # put etag in to db 
        self.authEtagService.store_userdata_etag_to_DB_handler(user_id=user_id,etag=etag)
        
        # put etag into cache
        self.cacheService.set(key=etag_key,time=3600,data=etag)
        
            
            
        data = ({'user_id':userid,'display_name':display_name,'user_name':username,'role':role,'avatar':avatar if avatar else None})
        return  data,etag
        