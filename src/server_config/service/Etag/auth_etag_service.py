from src.server_config.service.Etag.Etag import EtagService
from src.database.database_keys import DATABASEKEYS
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
