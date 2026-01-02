
from flask import Blueprint, request, jsonify
from src.token.tokenservice import TokenService
from src.trip_service.trip_service import TripService
from src.database.s3.s3_service import S3Sevice
from src.database.s3.s3_dirs import TRIP_DIR
from src.geo.geo_service import GeoService
from src.server_config.service.Etag.trip_data_etag import TripDataEtag
from src.database.trip_db_service import TripDatabaseService
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
        self.trip_s3 = S3Sevice()  
        self.geo_service = GeoService()
        self.trip_data_etag_service = TripDataEtag()
        self.trip_database_service = TripDatabaseService()
        self._init = True
        self._register_route()
    
    def _register_route(self):
        self.bp.route("/request-new-trip", methods=["POST"])(self.request_new_trip)
        self.bp.route('/trips',methods =['GET'])(self.request_all_trips_data)
        self.bp.route('/current-trip', methods=['GET'])(self.request_current_trip_data)
        self.bp.route("/end-trip",methods=["POST"])(self.end_trip)


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
        
        if not status :
            return jsonify({"message":message,"code":"failed"}),500
        else:
            self.trip_database_service.update_trips_version(user_id=user_id)
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
        status,message = self.trip_service.end_a_trip(trip_id=trip_id)
        if not status:
            return jsonify({"code":"failed","message":message}),500
        
        self.trip_database_service.update_trips_version(user_id=user_id)
        return jsonify({"code":"successfully","message":message}),200
   
    
    def request_current_trip_data(self):
        Ptoken = request.headers.get("Authorization")
        token=Ptoken.replace("Bearer ","")
        valid_token, Tmessage,code= self.token_service.jwt_verify(token)
        # return if jwt in valid or expried

        if not valid_token:
            return jsonify({"message":Tmessage, "code":code}),401
        data_from_jwt = self.token_service.decode_jwt(token=token)
        user_id  = data_from_jwt.get('user_id')
        client_etag = request.headers.get('If-Not-Match')
        current_trip_data,etag = self.trip_service.get_trip_data(user_id=user_id,client_etag=client_etag)
        if current_trip_data is None and etag is not None:
            return jsonify({'etag':etag}),304
        
        return jsonify({'message':'Successfully!','etag':etag,'current_trip_data':current_trip_data if current_trip_data else None}),200

    def request_all_trips_data(self):
        Ptoken = request.headers.get("Authorization")
        token=Ptoken.replace("Bearer ","")
        valid_token, Tmessage,code= self.token_service.jwt_verify(token)
        # return if jwt in valid or expried

        if not valid_token:
            return jsonify({"message":Tmessage, "code":code}),401
        client_etag = request.headers.get('If-Not-Match')
        client_version = request.headers.get('Version')
        data_from_jwt = self.token_service.decode_jwt(token=token)
        user_id  = data_from_jwt.get('user_id')
        
        all_trips_data,etag = self.trip_service.get_all_trip_data(user_id=user_id,client_etag=client_etag,client_version=client_version)
        
        if all_trips_data is None and etag is not None:
            return jsonify({'etag':etag}),304
        
        return jsonify({'message':'Successfully!','all_trip_data':all_trips_data if all_trips_data else None}),200
    
    
 