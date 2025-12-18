import jwt
from src.server_config.config import Config
from datetime import datetime , timedelta
from src.database.database import Database
class TokenService:
    def __init__(self):
        self.db = Database()
        self.config = Config()
    def generate_jwt(self, **kwargs): #days:00 // hours:00 // minutes:00
        #encode token using key and HS256
        exp_time = kwargs.pop("exp_time",{"days":30}) #if doesnt pass in, it will set as 30 days
        SECRET_KEY =self.config.private_key 
        token = jwt.encode({
            "user_id":kwargs.get("id"),
            "user_name":kwargs.get("username"),
            "display_name": kwargs.get("display_name"),
            "issue":int((datetime.utcnow().timestamp())),
            "exp":int((datetime.utcnow() + timedelta(**exp_time)).timestamp()) 
        },
        SECRET_KEY,
        algorithm='RS256'
        )
        assert token != None ,"Token Undefine!"
        return token
    def decode_jwt(self,token): 
        PUBLIC_KEY = self.config.public_key
        assert token is not None, "Some how token is none" 
        payload = jwt.decode(token, PUBLIC_KEY ,algorithms =["RS256"])
        data ={'user_id':payload["user_id"],'user_name':payload["user_name"],'display_name':payload["display_name"]}
        return data
    def jwt_verify(self,token):
        print("jwt verify get called!")
        print(token)
        PUBLIC_KEY = self.config.public_key
        try:
            payload = jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            options={"exp": True}  # make sure expiration is enforced
        )
            print("issue time: ",payload['issue'])
            print("exp time: ",payload['exp'])
            print("cur time: ",int(datetime.utcnow().timestamp()))
            if(int(datetime.utcnow().timestamp()))>payload['exp']: ##just doesnt believe in the jwt anymore =))
                return False, "Token Expired!"
            # user_data= {"user_id":payload["user_id"],"user_name":payload["user_name"]}  
        except jwt.InvalidTokenError:
            return False,"Token Invalid!"
        return True,"Successfully!"
    def refresh_token_verify(self,row):
        revoked_status = row[6]
        assert type(revoked_status) == bool ,"Revoked_status must be type bool"
        assert revoked_status != None ,"Revoked_status Null"
        if revoked_status ==True:
            return False
        if datetime.now() >= row[5]:
            self.revoked_refresh_token(userid=row[1])
            return False
        return True
        

    def revoked_refresh_token(self,**kwargs):
        userid = kwargs.get("userid")
        status = self.db.update_db(table ="tripin_auth.tokens", item ="user_id", value =userid, item_to_update = "revoked", value_to_update = True)
        assert status == True ,"Error trying to update database revoked_token"
 
    def request_new_access_token(self,refresh_token):
        row = self.db.find_item_in_sql(table="tripin_auth.tokens",item="token",value=refresh_token)
        new_token=None
        if row is None:
            return False, None
        if self.refresh_token_verify(row):
            new_token = self.generate_jwt(id=row[1],display_name = row[2],username=row[3],exp_time={"minutes":1})
            return True, new_token
        return False ,None
        