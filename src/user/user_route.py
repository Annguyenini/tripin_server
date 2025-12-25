from flask import Blueprint,request,jsonify 
from src.database.s3.s3_service import S3Sevice
from src.token.tokenservice import TokenService
from src.database.database import Database
from src.database.s3.s3_buckets import AVATAR_BUCKET
class UserRoute :
    _instance = None
    def __new__(cls):
        if not cls._instance:
           cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.bp= Blueprint('user',__name__)
        self.S3Service = S3Sevice()
        self.TokenService = TokenService()
        self.DatabaseService = Database()
        self._register_route()
    
    
    def _register_route(self):
        self.bp.route('/update-avatar',methods=["POST"])(self.update_profile_image)
    
    def update_profile_image(self):
        """update user avatar

        Returns:
            jsonify: json object , http code
        """
        # get token and verify token
        ptoken = request.headers.get('Authorization')
        
        token = ptoken.replace('Bearer ','')
        
        Ptoken = request.headers.get("Authorization")
        token=Ptoken.replace("Bearer ","")
        token_status, message, code = self.TokenService.jwt_verify(token=token)
        
        # return 401 if token is invalid or expired
        if not token_status:
            return jsonify({"message":message,'code':code}),401
        
        # get user data direcly from jwt
        data_from_jwt = self.TokenService.decode_jwt(token)
        user_id = data_from_jwt.get('user_id')
        
        # default path
        path = f'user{user_id}_avatar.jpg'
        
        
        # get image and return if not image
        image = request.files.get('image')
        if image is None:
            return jsonify({"message":"No Image Found",'code':'failed'}),401

        # upload to s3 and return 401 if error occurr
        s3_status = self.S3Service.upload_media(image_path=AVATAR_BUCKET+'/'+path,image=image)
        if not s3_status:
            return jsonify({"message":"Error Upload To Cloud",'code':'failed'}),500
        
        # write default avatar path to db and return 401 if error ocurr
        db_status = self.DatabaseService.update_db('tripin_auth.userdata','id',user_id,'avatar',path)
        if not db_status:
            return jsonify({"message":"Error Upload To Database",'code':'failed'}),500
        
        # return 200 
        return jsonify({'message':'Successfully', 'code':'successfully'}),200       
        
 