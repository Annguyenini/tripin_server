from flask import request   
from src.token.tokenservice import TokenService
class RouteBase:
    _instance = None
    _init = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    def __init__(self):
        if self._init : return
        self.tokenService = TokenService()
        self._init = True
    
    def _get_authenticated_user(self):
        # verify jwt 
        Ptoken = request.headers.get("Authorization")
        token=Ptoken.replace("Bearer ","")
        valid_token, message,code= self.tokenService.jwt_verify(token)
        # return if jwt in valid or expried
        if not valid_token:
            return None,{'message':message, 'code':code}
        
        user_data = self.tokenService.decode_jwt(token=token)
        print (user_data)
        return user_data,None
        