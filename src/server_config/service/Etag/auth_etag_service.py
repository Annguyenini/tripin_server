from src.server_config.service.Etag.Etag import EtagService
from src.database.database_keys import DATABASEKEYS
from src.server_config.service.cache import Cache
class AuthEtagService (EtagService):
    _instance = None
    _init = False
    def __new__(cls):
        if cls._instance is None :
            cls._instance = super().__new__(cls)
        return cls._instance
    
    
    def __init__(self):
        if self._init :
            return
        super().__init__()
        self.cacheService = Cache()
        self._init = True
        
    def generate_key(self,user_id:int)->str:
        return (f'user:{user_id}:userdata')
    
    def genarate_etag_string(self,user_id:int,version:int)->str:
        return (f'user:{user_id}:userdata:version{version}')
    
    def store_userdata_etag_to_DB_handler(self,user_id,etag:str):
        put_to_db = self.databaseService.update_db(DATABASEKEYS.TABLES.USERDATA,
                                       DATABASEKEYS.USERDATA.USER_ID,
                                       user_id,
                                       DATABASEKEYS.USERDATA.ETAG,
                                       etag)
        if not put_to_db:
            raise('Failed to insert etag into database!') 
        return 
    
    def get_userdata_etag_from_cache(self,key:str)->str:
        etag_cache = self.cacheService.get(key=key)
        return etag_cache
    
    def get_userdata_etag_from_database(self,user_id:int):
        con,cur = self.databaseService.connect_db()
        cur.execute(f'''SELECT {DATABASEKEYS.USERDATA.ETAG} FROM {DATABASEKEYS.TABLES.USERDATA} WHERE {DATABASEKEYS.USERDATA.USER_ID} = %s''',(user_id,))
        con.commit()
        db_etag = cur.fetchone()
        return db_etag if db_etag else None


    def userdata_etag_validation(self,user_id:int,client_etag:str)-> object:
        if not client_etag: return False,None
        etag_key = self.generate_key(user_id=user_id)
        cache_etag = self.get_userdata_etag_from_cache(key=etag_key)
        if cache_etag:
            if client_etag == cache_etag:
                return(True,cache_etag)
        else:
            # set the etag to cahche
            db_etag = self.get_userdata_etag_from_database(user_id=user_id)
            if db_etag:
                if client_etag == db_etag:
                    self.cacheService.set(key=etag_key,time=3600,data=db_etag)
                    return(True,db_etag)
        return False, None
        
    def generate_userdata_etag(self,user_id,userdata_version):
        etag_string = self.genarate_etag_string(user_id=user_id,version= userdata_version)
        etag = self.generate_etag(key=etag_string)
        return etag
        