##before pass into service fucntions, this help filter info and verify jwt token for unnesscary function call
##rate limit are set as 5 requests total per min


from flask import Blueprint, jsonify, request
from src.server_config.config import Config
from src.database.database import Database
from src.credential.credential import Auth
from src.token.tokenservice import TokenService
from src.server_config.encryption.encryption import Encryption
from src.server_auth.server_auth import ServerAuth
from src.server_config.service.cache import Cache
class AuthServer:
    _instance = None 
    def __new__(cls,*args,**kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    def __init__(self):
        self.bp = Blueprint("auth", __name__)
        self.auth = Auth()
        self.token_service = TokenService()
        self.encryption_service = Encryption()
        self.rate_limiter_service = Cache()
        self._register_routes()

    def _register_routes(self):
        
        """Auth Route 
            Each have rate limiter of 5 per minute in total            
        """
        # pass the bound method
        ##rate limiter
        @self.bp.before_request
        def rate_limit():
            user_ip = request.remote_addr
            count = self.rate_limiter_service.incr(user_ip)
            if count ==1:
                self.rate_limiter_service.exp(user_ip,60)
            elif count>5:
                return jsonify({"message":"Too many request!"}),429
            
            
        self.bp.route("/login-via-token", methods=["POST"])(self.login_via_token)
        self.bp.route("/login", methods=["POST"])(self.login)
        self.bp.route("/signup", methods=["POST"])(self.signup)
        self.bp.route("/request-access-token", methods=["POST"])(self.request_new_access_token)
        self.bp.route("/verify-code", methods=["POST"])(self.verify_code)

    def verify_code(self):
        """User verify code, get user data and pass to a function to check the code

        """
        data = request.json
        recipients = data.get("email")
        email= recipients.lower()
        str_code = data.get("code")
        code = int(str_code)
        respond = self.auth.confirm_code(email,code)

        if not respond:
            return jsonify({"status":"Failed"}),500

        return jsonify({"status":"Successfully"}),200

    def login_via_token(self): 
        """
        Docstring for login_via_token
        
        :param self: get token from header verify token 
        """      
        ptoken = request.headers.get("Authorization")
        token = ptoken.replace("Bearer ", "")
        data = self.auth.login_via_token(token=token)
        status = data['status']
        message = data['message']
        code = data['code']
        user_data = data['user_data']
    
        if not status:
            return jsonify({"message": message,"user_data": None,"code":code}), 401
        return jsonify({"message": message, "user_data": user_data}), 200

    def login(self):
        data = request.json
        username = data.get("username")
        password = data.get("password")
        login_process= self.auth.login(username=username, password=password)
        status = login_process['status']
        message = login_process['message']
        user_data = login_process['user_data']
        tokens = login_process['tokens']
        if not status:
            return jsonify({"message": message}), 401
        return jsonify({"message": message,'tokens':tokens, "user_data": user_data }), 200

    def signup(self):
        data = request.json
        email = data.get("email")
        display_name = data.get("displayName")
        username = data.get("username")
        password = data.get("password")
        lower_case_email = email.lower()
        status, message = self.auth.signup(email=lower_case_email, display_name=display_name, username=username, password=password)
        if not status:
            return jsonify({"message": message}), 401
        return jsonify({"message": message}), 200

    def request_new_access_token(self):
        data = request.headers.get("Authorization")
        token = data.replace("Bearer ", "")
        status, new_token = self.token_service.request_new_access_token(token)
        if not status:
            return jsonify({"message": "Could not finish the request!"}), 401
        return jsonify({"message": "Successfully", "token": new_token}), 200