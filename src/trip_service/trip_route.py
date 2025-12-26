
from flask import Blueprint, request, jsonify
from src.token.tokenservice import TokenService
from src.trip_service.trip_service import TripService
from src.database.s3.s3_service import S3Sevice
from src.database.s3.s3_dirs import TRIP_DIR
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
        self._register_route()
    
    def _register_route(self):
        self.bp.route("/request-new-trip", methods=["POST"])(self.request_new_trip)
        self.bp.route("/<trip_id>/coordinates",methods =["POST"])(self.add_coordinates)
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
            upload = self.trip_s3.upload_media(image_path=image_path,image=image)
        
        if not status:
            print(message)
            return jsonify({"message":message,"code":"failed"}),401
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

        trip_id = user_data.get("trip_id")        
        print(trip_id,type(trip_id))
        status,message = self.trip_service.end_a_trip(trip_id=trip_id)
        if not status:
            return jsonify({"code":"failed","message":message}),500
        return jsonify({"code":"successfully","message":message}),200
   
   
    def add_coordinates(self,trip_id):
        """handler from the client

        Returns:
            status code: 
        """
        # get the request data
        data =request.json
        # verify jwt 
        Ptoken = request.headers.get("Authorization")
        token=Ptoken.replace("Bearer ","")
        valid_token, Tmessage,code= self.token_service.jwt_verify(token)
        
        # return if jwt in valid or expried
        if not valid_token:
            return jsonify({"message":Tmessage, "code":code}),401
        coordinates = data.get("coordinates")
        # insert coordinates into server db
        insert = self.trip_service.insert_coordinates_to_db(trip_id=trip_id,coordinates=coordinates)
        
        if not insert:
            return jsonify({"code": "failed", "message":"Failed to save to database"}),500
        
        return jsonify({"code": "successfully", "message":"Successfully store into database"}),200