import jwt
from src.server_config.config import Config
from datetime import datetime , timedelta
from src.database.database import Database
class TokenService:
    def __init__(self):
        self.db = Database()
        self.config = Config()



    def generate_jwt(self, user_id:int,role:str ='user',exp_time ={'days':30}): #days:00 // hours:00 // minutes:00
        """generate jwt

        Args:
            user_id (int): user_id
            user_name (str): user name
            display_name (str): display name
            sub (str): subcription
            role (str, optional): user role. Defaults to 'user'.
            exp_time (dict, optional): duration. Defaults to {'days':30}.

        Returns:
            _type_: _description_
        """
        #encode token using key and HS256
        SECRET_KEY =self.config.private_key 
        token = jwt.encode({
            "user_id":user_id,
            "role": role,
            "issue":int((datetime.utcnow().timestamp())),
            "exp":int((datetime.utcnow() + timedelta(**exp_time)).timestamp()) 
        },
        SECRET_KEY,
        algorithm='RS256'
        )
        assert token != None ,"Token Undefine!"
        return token
    def decode_jwt(self,token): 
        """decode to get data

        Args:
            token (string): access token

        Returns:
            object:data 
        """
        PUBLIC_KEY = self.config.public_key
        assert token is not None, "Some how token is none" 
        payload = jwt.decode(token, PUBLIC_KEY ,algorithms =["RS256"])
        data ={'user_id':payload["user_id"],'role':payload['role']}
        return data
    def jwt_verify(self,token:str):
        """verify token

        Args:
            token (string): access_token

        Returns:
            boolean: status
            message: Message
            code: verify code status
        """

        PUBLIC_KEY = self.config.public_key
        try:
            payload = jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            options={"exp": True}  # make sure expiration is enforced
        )
            # print("issue time: ",payload['issue'])
            # print("exp time: ",payload['exp'])
            # print("cur time: ",int(datetime.utcnow().timestamp()))
            if(int(datetime.utcnow().timestamp()))>payload['exp']: ##just doesnt believe in the jwt anymore =))
                return False, "Token Expired!","token_expired"
            # user_data= {"user_id":payload["user_id"],"user_name":payload["user_name"]}  
        except jwt.InvalidTokenError:
            return False,"Token Invalid!","token_invalid"
        return True,"Successfully!","successfully"
    def refresh_token_verify(self,refresh_token):
        """verify refresh token

        Args:
            row (_type_): _description_

        Returns:
            _type_: _description_
        """
        row = self.db.find_item_in_sql(table="tripin_auth.tokens",item="token",value=refresh_token)
        revoked_status = row['revoked']
        assert type(revoked_status) == bool ,"Revoked_status must be type bool"
        assert revoked_status != None ,"Revoked_status Null"
        if revoked_status ==True:
            return False
        if datetime.now() >= row['expired_at']:
            self.revoked_refresh_token(userid=row['user_id'])
            return False
        return True
        

    def revoked_refresh_token(self,**kwargs):
        
        userid = kwargs.get("userid")
        status = self.db.update_db(table ="tripin_auth.tokens", item ="user_id", value =userid, item_to_update = "revoked", value_to_update = True)
        assert status == True ,"Error trying to update database revoked_token"
        

 
    def request_new_access_token(self,refresh_token:str):
        if not self.refresh_token_verify(refresh_token):
            return False, None
        
        data_from_jwt = self.decode_jwt(refresh_token)
        user_id=data_from_jwt['user_id']

        role = data_from_jwt['role']
       
        new_token = self.generate_jwt(user_id=user_id,role=role,exp_time={'minutes':1})
        return True,new_token