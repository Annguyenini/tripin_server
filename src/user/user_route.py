from flask import Blueprint,request,jsonify 
from src.database.s3.s3_service import S3Sevice
from src.token.tokenservice import TokenService
from src.database.database import Database
from src.database.s3.s3_dirs import AVATAR_DIR
from src.user.user_service import UserService
from src.database.database_keys import DATABASEKEYS
from src.database.userdata_db_service import UserDataDataBaseService
from src.base.route_base import RouteBase
class UserRoute (RouteBase):
    _instance = None
    def __new__(cls):
        if not cls._instance:
           cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        super().__init__()
        self.bp= Blueprint('user',__name__)
        self.S3Service = S3Sevice()
        self.TokenService = TokenService()
        self.DatabaseService = Database()
        self.UserService = UserService()
        self.UserDataBaseService = UserDataDataBaseService()
        self._register_route()
    
    
    def _register_route(self):
        self.bp.route('/update-avatar',methods=["POST"])(self.update_profile_image)
        self.bp.route('/get-user-data',methods=['GET'])(self.get_user_data)
    
    def get_user_data(self):
        user_data,error = self._get_authenticated_user()
        if error :
            return jsonify(error),401
        user_id_from_jwt = user_data.get('user_id')
        
        client_etag = request.headers.get('If-None-Match')
        
        user_data,etag = self.UserService.get_user_data_from_database(user_id=user_id_from_jwt,client_etag=client_etag)
        
        if user_data is None and etag:
            return jsonify({'etag':etag,'message':'Successfully'}),304
        
        return jsonify({'user_data':user_data,'message':'Successfully','etag':etag}),200
        
    
    
    def update_profile_image(self):
        """update user avatar

        Returns:
            jsonify: json object , http code
        """
        # get token and verify token
        
        user_data,error = self._get_authenticated_user()
        if error :
            return jsonify(error),401
        
        # get user data direcly from jwt
        user_id = user_data.get('user_id')
        
        # get image and return if not image
        image = request.files.get('image')
        if image is None:
            return jsonify({"message":"No Image Found",'code':'failed'}),401

        # upload to s3 and return 401 if error occurr
        upload = self.UserService.update_user_avartar(user_id=user_id,image=image)
        # return 200 
        if not upload['status']:
            return jsonify(upload),500  
        return jsonify(upload),200       
        
 