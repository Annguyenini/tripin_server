from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime,timedelta
from src.database.database import Database
from src.server_config.config import Config
from src.token.tokenservice import TokenService
from src.mail.mail_service import MailService
from src.database.s3.s3_service import S3Sevice
from src.trip_service.trip_service import TripService
from src.user.user_service import UserService
from src.database.s3.s3_dirs import AVATAR_DIR, TRIP_DIR    
from src.server_config.service.cache import Cache
from src.server_config.service.Etag.Etag import EtagService
from src.server_config.service.Etag.auth_etag_service import AuthEtagService
from src.database.database_keys import DATABASEKEYS
from src.server_config.service.input_validation import InputValidation
#userdata user_id|email|user_name|displayname|password
#token keyid| userid| username|token|issue name | exp name | revok
class Auth:
    _instance = None 
    _initialize =False
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    def __init__(self):
        if not self._initialize:
            self.db = Database()
            self.tokenService = TokenService()
            self.mail_service = MailService()
            self.s3Service = S3Sevice()
            self.tripService = TripService()
            self.userService = UserService()
            self.cacheService = Cache()
            self.etagService = EtagService()
            self.authEtagService = AuthEtagService()
            self.inputValidationService = InputValidation()
            self.user_queue = {}
            self._initialize = True
    #login function
    def login(self,username:str,password:str):
        """Login fuction use for process call jwt generate, verify credential 

        Returns:
            bool : status
            tuple: user_id|display_name|user_name|refresh_token|access_token|role
            tuple:
        """
        #verify user input 
        if not self.inputValidationService.username_validation(username=username): return False,({'message':'invalid username'})
        if not self.inputValidationService.password_validation(password=password) :return False,({'message':'invalid password'})
        
    
        ##find username in database
        
        userdata_row = self.db.find_item_in_sql(table="tripin_auth.userdata",item="user_name",value=username)
        
        ##return false if username not exist
        if userdata_row is None:
            return (False,{'message':"Wrong username",'user_data':None})
        
        userid=userdata_row["id"] 
        # checker
        assert userid is not None ,"UserID Null"
        role = userdata_row["role"]

        # if user is found and password is correct
        if not check_password_hash(userdata_row["password"],password): # password
            return (False,{'message':"Wrong password",'user_data':None,'trip_data':None,'tokens':None,'all_trip_data':None})
        

        # user data 
        user_data = {'user_id':userid,'role':role}
                
        # old token got revoked
        self.tokenService.revoked_refresh_token(userid=userid)
        
        
        #new tokens generated
        refresh_token = self.tokenService.generate_jwt(user_id=userid,role=role)
        access_token = self.tokenService.generate_jwt(user_id=userid,role=role,exp_time={"minutes":1})
        token_data ={'access_token':access_token,'refresh_token':refresh_token}
        
        ##inserted token into database
        self.db.insert_token_into_db(
            user_id =userdata_row["id"],
            username=username,
            token=refresh_token,
            issued_at=datetime.utcnow(),
            expired_at = datetime.utcnow() + timedelta(days=30),
            )
       
        return (True,{'message':"Successfully",'user_data':user_data,'tokens':token_data})
    #signup function
    def signup(self,email:str,display_name:str,username:str,password:str): 
        
        if not self.inputValidationService.email_validation(email=email): return False, 'invalid email'
        if not self.inputValidationService.username_validation(username=username): return False, 'invalid username'
        if not self.inputValidationService.displayname_validation(display_name=display_name) :return False, 'invalid display name'
        if not self.inputValidationService.password_validation(password=password):return False ,'invalid password'
        ##hash password, prepare to insert to database 
        hashed_passwords = generate_password_hash(password)
        # print(email,display_name,username,hashed_passwords)
        #check if email or username already exists
        
        ## if the Email already exists in database, return 
        if(self.db.find_item_in_sql(table="tripin_auth.userdata",item="email",value=email)):
            return False, "Email already exists!"
       
        ## if the username already exists in database, return  
        if(self.db.find_item_in_sql(table="tripin_auth.userdata",item="user_name",value=username)):
            return False, "Username already exists!"
        
        ## process to verify email
        respond = self.mail_service.send_confirmation_code(email)
        
        if(respond):
            data={
                "email":email,
                "display_name":display_name,
                "username":username,
                "password":hashed_passwords,
            }
            self.user_queue[email] = data
            return True, "Successfully"
        else :
            return False,"Error at signup"
    
   
   
    def login_via_token (self,token:str):
        status, message,code = self.tokenService.jwt_verify(token)
        # print(status,message,code
        # if token invalid or expried, return
        if not status:
            return ({'status':False,"message": message,"code":code,"user_data": None,'trip_data':None,'all_trip_data':None})
        
        # get userdata from token
        userdata_from_jwt = self.tokenService.decode_jwt(token)  
        
        user_id=userdata_from_jwt["user_id"] 
        role = userdata_from_jwt['role']
        
        user_data = {'user_id':user_id,'role':role}
        
        return ({'status':True,"message": message, "user_data": user_data,"code":code})
    
    
    
    
    def process_new_user(self,email:str):
        assert(type(email) is not str,"Email should be string")
        data =  self.user_queue.get(email)
        display_name = data.get ("display_name")
        username = data.get("username")
        password = data.get("password")
        res = self.db.insert_to_database_singup(email=email, display_name=display_name,username=username,password=password)
        if res< 0:
            return False
        return True
    
    def confirm_code(self, email:str, code:str):
        respond = self.mail_service.verify_code(recipients=email,code=code)
        if not respond:
            return False
        process_new_user = self.process_new_user(email=email)
        if not process_new_user:
            return False
        return True
    
