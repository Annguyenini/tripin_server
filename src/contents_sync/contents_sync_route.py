from flask import Blueprint, jsonify,request
from src.database.trip_db_service import TripDatabaseService
from src.database.database_keys import DATABASEKEYS
from src.server_config.service.token_validation import token_validation
from src.token.tokenservice import TokenService
from src.error_code.error_code import ERROR_KEYS ,ERROR_MESSAGE
from src.base.route_base import RouteBase
from src.trip_service.trip_contents.trip_contents_service import TripContentService

class ContentsSyncRoute (RouteBase):
    _instance = None
    _init = False
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    def __init__(self):
        if self._init :return
        super().__init__()
        self.bp = Blueprint('sync',__name__)
        self.tripDataBaseService = TripDatabaseService()
        self.tokenService = TokenService()
        self.trip_contents_service = TripContentService()
        self._register_route()
        self._init = True
        
        
    def _register_route(self):
        self.bp.route('/trip-coordinate-version',methods=['POST'])(self.get_trip_coordinate_version)        
        self.bp.route('/trip-medias-hash',methods=['POST'])(self.get_trip_medias_hash)
        self.bp.route('/trip-medias-metadata',methods=['POST'])(self.get_trip_media_metadata)
    
    
    def get_trip_coordinate_version(self):
        user_data,error = self._get_authenticated_user()
        if error:
            return (error),401
        trip_id = request.json['trip_id']      
        coordinates_version = self.tripDataBaseService.get_trip_contents_version(trip_id=trip_id,version_type=DATABASEKEYS.TRIPS.TRIP_COORDINATES_VERSION)
        return jsonify({'coordinates_version':coordinates_version}),200
    
    
    def get_trip_medias_hash(self):
        
        user_data,error = self._get_authenticated_user()
        if error:
            return (error),401
        user_id = user_data ['user_id']
        trip_id = request.json['trip_id']
        trip_validation =self.tripDataBaseService.trip_owner_validation(user_id=user_id,trip_id=trip_id)
        if not trip_validation:
            return jsonify({'code':ERROR_KEYS.NOPERMISSION,'message':ERROR_MESSAGE.NOPERMISSION}),403
        media_hash = self.trip_contents_service.get_trip_medias_hash(trip_id=trip_id)
        if not media_hash:
            return jsonify({'code':ERROR_KEYS.FAILED,'message':ERROR_MESSAGE.SERVER_FAILED}) ,500
        return jsonify({'hash':media_hash,'trip_id':trip_id})
    
    def get_trip_media_metadata(self):
        user_data,error = self._get_authenticated_user()
        if error:
            return (error),401
        user_id = user_data ['user_id']
        trip_id = request.json['trip_id']
        trip_validation =self.tripDataBaseService.trip_owner_validation(user_id=user_id,trip_id=trip_id)
        if not trip_validation:
            return jsonify({'code':ERROR_KEYS.NOPERMISSION,'message':ERROR_MESSAGE.NOPERMISSION}),403
        metadata = self.trip_contents_service.get_trip_media_metadata(trip_id=trip_id)
        if not metadata:
            return jsonify({'code':ERROR_KEYS.FAILED,'message':ERROR_MESSAGE.SERVER_FAILED}) 
        return jsonify({'metadata':metadata,'trip_id':trip_id})