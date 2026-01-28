
from flask import Blueprint, request, jsonify
from src.token.tokenservice import TokenService
from src.trip_service.trip_service import TripService
from src.trip_service.trip_contents.trip_contents_service import TripContentService
from src.database.s3.s3_service import S3Sevice
from src.database.s3.s3_dirs import TRIP_DIR
from src.geo.geo_service import GeoService
from src.database.trip_db_service import TripDatabaseService
from src.server_config.service.cache import Cache
import json
class TripRoute:
    _instance = None
    _init =False
    def __new__(cls,*args,**kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init: return
        self.bp = Blueprint('trip',__name__)
        self.token_service = TokenService()     
        self.trip_service = TripService() 
        self.trip_content_service = TripContentService()
        self.trip_s3 = S3Sevice()  
        self.geo_service = GeoService()
        self.cache_service = Cache()
        self.trip_database_service = TripDatabaseService()
        self._init = True
        self._register_route()
    
    def _register_route(self):
        self.bp.route("/request-new-trip", methods=["POST"])(self.request_new_trip)
        self.bp.route('/trips',methods =['GET'])(self.request_all_trips_data)
        self.bp.route('/current-trip-id', methods=['GET'])(self.request_current_trip_id)
        self.bp.route("/end-trip",methods=["POST"])(self.end_trip)
        self.bp.route('/trip',methods=['POST'])(self.request_trip_data)

    ## request new trip
    def request_new_trip(self):
        
        """take in user data to process new trip

        Returns:
            status: html status, message
        """
        Ptoken = request.headers.get("Authorization")
        token=Ptoken.replace("Bearer ","")
        
        ##verify token
        valid_token,Tmessage,code = self.token_service.jwt_verify(token)
        ##return if invalid token
        if not valid_token:
            print(code)
            return jsonify ({"message":Tmessage,"code":code}), 401
        
        ##decode jwt to get userdatas
        user_data_from_jwt = self.token_service.decode_jwt(token)
        user_id = user_data_from_jwt.get("user_id")
        trip_name = request.form.get("trip_name")
                
        #process new trip
        
        #get image, and image_path
        image = request.files.get('image')
        image_path =None
        status, message,trip_id = self.trip_service.process_new_trip(user_id,trip_name,image_path,image=image)
        
        if image:   
            image_path = f"trips/{trip_id}/cover.jpg"
            # upload to s3
            upload = self.trip_s3.upload_media(path=image_path,data=image)            
            upload_image = self.trip_content_service.upload_trip_image(trip_id,image_path=image_path)

        
        if not status :
            return jsonify({"message":message,"code":"failed"}),500
        else:
            return jsonify({"message":message,"trip_id":trip_id,"code":"successfully"}),200
   
    def end_trip(self):
        """handle end trip

        Returns:
            json: return to client
        """
        user_data = request.json

        Ptoken = request.headers.get("Authorization")
        token=Ptoken.replace("Bearer ","")
        
        ##verify token
        valid_token,Tmessage,code = self.token_service.jwt_verify(token)
        ##return if invalid token
        if not valid_token:
            return jsonify ({"message":Tmessage,"code":code}), 401
        
        ##decode jwt to get userdatas
        user_data_from_jwt = self.token_service.decode_jwt(token)
        user_id = user_data_from_jwt['user_id']
        trip_id = user_data.get("trip_id")        
        status,message = self.trip_service.end_a_trip(trip_id=trip_id,user_id=user_id)
        if not status:
            return jsonify({"code":"failed","message":message}),500
        
        return jsonify({"code":"successfully","message":message}),200
   
    
    def request_current_trip_id(self):
        Ptoken = request.headers.get("Authorization")
        token=Ptoken.replace("Bearer ","")
        valid_token, Tmessage,code= self.token_service.jwt_verify(token)
        # return if jwt in valid or expried

        if not valid_token:
            return jsonify({"message":Tmessage, "code":code}),401
        decoded_data = self.token_service.decode_jwt(token=token)
        user_id = decoded_data['user_id']
        current_trip_id = self.trip_service.get_current_trip_id(user_id=user_id)
        return jsonify({'current_trip_id':current_trip_id}),200
    
    def request_trip_data(self):
        Ptoken = request.headers.get("Authorization")
        token=Ptoken.replace("Bearer ","")
        valid_token, Tmessage,code= self.token_service.jwt_verify(token)
        # return if jwt in valid or expried

        if not valid_token:
            return jsonify({"message":Tmessage, "code":code}),401
        data_from_jwt = self.token_service.decode_jwt(token=token)
        
        
        user_id  = data_from_jwt.get('user_id')
        client_etag = request.headers.get('If-None-Match')
        trip_id = request.json.get('trip_id')
        trip_data,etag = self.trip_service.get_trip_data(user_id=user_id,trip_id=trip_id,client_etag=client_etag)
        if trip_data is None and etag is not None:
            return jsonify({'etag':etag}),304
        
        if not trip_data and not etag:
            return jsonify({'message':'failed'}),404
        
        return jsonify({'message':'Successfully!','etag':etag,'trip_data':trip_data if trip_data else None}),200

    def request_all_trips_data(self):
        Ptoken = request.headers.get("Authorization")
        token=Ptoken.replace("Bearer ","")
        valid_token, Tmessage,code= self.token_service.jwt_verify(token)
        # return if jwt in valid or expried

        if not valid_token:
            return jsonify({"message":Tmessage, "code":code}),401
        client_etag = request.headers.get('If-None-Match')
        data_from_jwt = self.token_service.decode_jwt(token=token)
        user_id  = data_from_jwt.get('user_id')
        
        all_trips_data,etag = self.trip_service.get_all_trip_data(user_id=user_id,client_etag=client_etag)

        
        if all_trips_data is None and etag:
            return jsonify({'etag':etag}),304
        
        return jsonify({'message':'Successfully!','etag':etag,'all_trip_data':all_trips_data if all_trips_data else None}),200
    
  