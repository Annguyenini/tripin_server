from flask import Blueprint, jsonify,request
from src.database.trip_db_service import TripDatabaseService
from src.database.database_keys import DATABASEKEYS
from src.server_config.service.token_validation import token_validation
from src.token.tokenservice import TokenService
class ContentsSyncRoute :
    _instance = None
    _init = False
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    def __init__(self):
        if self._init :return
        self.bp = Blueprint('sync',__name__)
        self.tripDataBaseService = TripDatabaseService()
        self.tokenService = TokenService()
        self._register_route()
        self._init = True
    def _register_route(self):
        self.bp.route('/trip-data-version',methods=['POST'])(self.get_trip_data_version)        
    
    def get_trip_data_version(self):
        token = request.headers['Authorization']
        Ptoken = token.replace('Bearer ','')
        status,message,code = self.tokenService.jwt_verify(Ptoken)
        if not status :
            return jsonify({'message':message,'code':code}),401  
        trip_id = request.json['trip_id']      
        information_version = self.tripDataBaseService.get_trip_contents_version(trip_id=trip_id,version_type=DATABASEKEYS.TRIPS.TRIP_INFO_VERSION)
        coordinates_version = self.tripDataBaseService.get_trip_contents_version(trip_id=trip_id,version_type=DATABASEKEYS.TRIPS.TRIP_COORDINATES_VERSION)
        medias_version = self.tripDataBaseService.get_trip_contents_version(trip_id=trip_id,version_type=DATABASEKEYS.TRIPS.TRIPS_MEDIAS_VERSION)
        return jsonify({'information_version':information_version,'medias_version':medias_version,'coordinates_version':coordinates_version}),200
    