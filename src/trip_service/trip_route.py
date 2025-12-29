
from flask import Blueprint, request, jsonify
from src.token.tokenservice import TokenService
from src.trip_service.trip_service import TripService
from src.database.s3.s3_service import S3Sevice
from src.database.s3.s3_dirs import TRIP_DIR
from src.geo.geo_service import GeoService
import json
class TripRoute:
    _instance = None
    def __new__(cls,*args,**kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.bp = Blueprint('trip',__name__)
        self.token_service = TokenService()     
        self.trip_service = TripService() 
        self.trip_s3 = S3Sevice()  
        self.geo_service = GeoService()
        self._register_route()
    
    def _register_route(self):
        self.bp.route("/request-new-trip", methods=["POST"])(self.request_new_trip)
        self.bp.route("/<trip_id>/coordinates",methods =["POST"])(self.add_coordinates)
        self.bp.route('/trips',methods =['GET'])(self.request_trips_data)
        self.bp.route ('/<trip_id>/upload',methods=['POST'])(self.media_upload)
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
        user_name = user_data_from_jwt.get("user_name")
        trip_name = request.form.get("trip_name")
                
        #process new trip
        
        #get image, and image_path
        image = request.files.get('image')
        image_path =None
        status, message,trip_id = self.trip_service.process_new_trip(user_id,trip_name,image_path)

        
        if image:   
            image_path = f"trips/{trip_id}/cover.jpg"
            # upload to s3
            upload = self.trip_s3.upload_media(path=image_path,data=image)
            upload_image = self.trip_service.upload_trip_image(trip_id,image_path=image_path)
        
        all_trip_data = self.trip_service.get_all_trip_data(user_id=user_id)
        if not status or not upload or not upload_image:
            if(not upload):
                message +='Failed to upload into cloud'
            if(not upload_image):
                message +='Failed to upload into db'
                
            print(message)

            return jsonify({"message":message,"code":"failed"}),500
        else:
            return jsonify({"message":message,"trip_id":trip_id,'all_trip_data':all_trip_data,"code":"successfully"}),200
   
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

        trip_id = user_data.get("trip_id")        
        status,message = self.trip_service.end_a_trip(trip_id=trip_id)
        if not status:
            return jsonify({"code":"failed","message":message}),500
        return jsonify({"code":"successfully","message":message}),200
   
   
    def add_coordinates(self,trip_id):
        """handler from the client

        Returns:
            status code: 
        """
       
        
        # verify jwt 
        Ptoken = request.headers.get("Authorization")
        token=Ptoken.replace("Bearer ","")
        valid_token, Tmessage,code= self.token_service.jwt_verify(token)
        # return if jwt in valid or expried

        if not valid_token:
            return jsonify({"message":Tmessage, "code":code}),401
        
        
        # get the request data
        data =request.json
        coordinates = data.get("coordinates")
        data_from_jwt = self.token_service.decode_jwt(token=token)
        user_id = data_from_jwt['user_id']
        
        longitude = data.get('longitude')
        latitude =data.get('latitude')
        # print('long',longitude,'lat',latitude)
        # insert coordinates into server db
        insert = self.trip_service.insert_coordinates_to_db(trip_id=trip_id,coordinates=coordinates)
        
        geo_data = None
        city = None
        if longitude and latitude:
            geo_data = self.geo_service.get_geo_data(longitude=longitude,latitude=latitude)
            
            city = self.geo_service.get_city(user_id=user_id,longitude=longitude,latitude=latitude)
            
        if not insert:
            return jsonify({"code": "failed", "message":"Failed to save to database"}),500
        
        return jsonify({"code": "successfully",'geo_data':geo_data, 'city':city, "message":"Successfully store into database"}),200
    
    def request_trips_data(self):
        Ptoken = request.headers.get("Authorization")
        token=Ptoken.replace("Bearer ","")
        valid_token, Tmessage,code= self.token_service.jwt_verify(token)
        # return if jwt in valid or expried

        if not valid_token:
            return jsonify({"message":Tmessage, "code":code}),401
        data_from_jwt = self.token_service.decode_jwt(token=token)
        user_id  = data_from_jwt.get('user_id')
        current_trip_data = self.trip_service.get_trip_data(user_id=user_id)
        all_trips_data = self.trip_service.get_all_trip_data(user_id=user_id)
        return jsonify({'message':'Successfully!','current_trip_data':current_trip_data if current_trip_data else None,'all_trip_data':all_trips_data if all_trips_data else None})
    
    
    def media_upload(self,trip_id):
        Ptoken = request.headers.get("Authorization")
        token=Ptoken.replace("Bearer ","")
        valid_token, Tmessage,code= self.token_service.jwt_verify(token)
        # return if jwt in valid or expried

        if not valid_token:
            return jsonify({"message":Tmessage, "code":code}),401
        data = json.loads(request.form.get('data'))
        print(data)
        longitude = data.get('longitude')
        latitude = data.get('latitude')
        time = data.get('time_stamp')  
        image = request.files.get('image')
        if image:
            path = image.filename
            upload_status = self.trip_service.upload_media('image',path=path,media=image,longitude=longitude,latitude=latitude,trip_id=trip_id,time=time)
        else:
            video = request.files.get('video')
            path = video.filename
            upload_status = self.trip_service.upload_media('video',path=path,media=video,longitude=longitude,latitude=latitude,trip_id=trip_id,time=time)
        
        if not upload_status:
            return jsonify({'message':'Failed!'}),500
        return jsonify({'message':'Successfully'})