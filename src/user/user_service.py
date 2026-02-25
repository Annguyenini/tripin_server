from src.database.database import Database
from src.database.database_keys import DATABASEKEYS
from src.database.s3.s3_service import S3Sevice
from src.server_config.service.Etag.auth_etag_service import AuthEtagService
from src.server_config.service.cache import Cache
from src.database.s3.s3_dirs import AVATAR_DIR
from src.database.userdata_db_service import UserDataDataBaseService

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
        self.UserDataBaseService =UserDataDataBaseService()
        self._init =True
    
    def get_user_data_from_database(self,user_id:int,client_etag:str = None)->object:
         
        # check etag in cache         
        etag_va_stat, etag = self.authEtagService.userdata_etag_validation(user_id=user_id,client_etag=client_etag)
        if etag_va_stat : return None, etag
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
            avatar = self.s3Service.generate_temp_uri(key=f'avatar/'+avatar)
            
            
        etag_key = self.authEtagService.generate_key(user_id=user_id)
        etag = self.authEtagService.generate_userdata_etag(user_id=user_id,userdata_version=userdata_version)
        
        
        # put etag in to db 
        self.authEtagService.store_userdata_etag_to_DB_handler(user_id=user_id,etag=etag)
        
        # put etag into cache
        self.cacheService.set(key=etag_key,time=3600,data=etag)
        
            
            
        data = ({'user_id':userid,'display_name':display_name,'user_name':username,'role':role,'avatar':avatar if avatar else None})
        return  data,etag

    def update_user_avartar(self,user_id:int,image):
        # default path
        path = f'user{user_id}_avatar.jpg'
        s3key =AVATAR_DIR+path
        s3_status = self.s3Service.upload_media(path=s3key,data=image)
        if not s3_status:
            return ({'status':False,"message":"Error Upload To Cloud",'code':'failed'})
        
        # write default avatar path to db and return 401 if error ocurr
        db_status = self.databaseService.update_db('tripin_auth.userdata','id',user_id,'avatar',path)
        up_version_stat,userdata_version = self.UserDataBaseService.update_userdata_version(user_id= user_id)
        if not db_status or not up_version_stat:
            return ({'status':False,"message":"Error Upload To Database",'code':'failed'})
        etag_key = self.authEtagService.generate_key(user_id=user_id)
        etag = self.authEtagService.generate_userdata_etag(user_id=user_id,userdata_version=userdata_version)
        
        
        # put etag in to db 
        self.authEtagService.store_userdata_etag_to_DB_handler(user_id=user_id,etag=etag)
        
        # put etag into cache
        self.cacheService.set(key=etag_key,time=3600,data=etag)
        return ({'status':True,'message':'Successfully','code':'successfully','etag':etag})
        print(db_status,up_version_stat)