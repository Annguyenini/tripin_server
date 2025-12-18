
from flask import Blueprint, request, jsonify
from src.token.tokenservice import TokenService
from src.trip_service.trip_service import TripService
class TripRoute:
    _instance = None
    def __new__(cls,*args,**kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.bp = Blueprint('mail',__name__)
        self.token_service = TokenService()     
        self.trip_service = TripService()   
        self._register_route()
    
    def _register_route(self):
        self.bp.route("/request-new-trip", methods=["POST"])(self.request_new_trip)
    
    ## request new trip
    def request_new_trip(self):
        
        """take in user data to process new trip

        Returns:
            status: html status, message
        """
        user_data = request.json
        token = request.headers.get("Authorization")
        token.replace("Bearer ","")
        
        ##verify token
        valid_token,Tmessage = self.token_service.jwt_verify(token)
        ##return if invalid token
        if not valid_token:
            return (Tmessage), 401
        
        ##decode jwt to get userdatas
        user_data_from_jwt = self.token_service.decode_jwt(token)
        user_id = user_data_from_jwt.get("user_id")
        user_name = user_data_from_jwt.get("user_name")
        trip_name = user_data.get("trip_name")
        
        #process new trip
        status, message,tripid = self.trip_service.process_new_trip(user_id,trip_name,)
        if not status :
            return jsonify({"message":message}),401
        else:
            return jsonify({"message":message,"tripid":tripid}),200