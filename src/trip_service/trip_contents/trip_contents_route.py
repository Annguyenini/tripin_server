from flask import jsonify,Blueprint,request
from src.token.tokenservice import TokenService
from src.trip_service.trip_contents.trip_contents_service import TripContentService
from src.geo.geo_service import GeoService
from src.server_config.service.smart_cast import smart_cast
from src.database.trip_db_service import TripDatabaseService
from src.database.trip_content_db_service  import TripContentsDatabaseService
from src.base.route_base import RouteBase
import json
class TripContentsRoute(RouteBase):
    _instance = None
    _init = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._init:
            return     
        super().__init__()
        self.bp = Blueprint('trip-contents',__name__)
        self.token_service = TokenService()     
        self.trip_contents_service = TripContentService() 
        self.geo_service = GeoService()
        self.trip_data_base_service= TripDatabaseService()
        self.trip_content_database_service = TripContentsDatabaseService()
        self._register_route()

        self._init =True
    def _register_route(self):
        self.bp.route ('/<trip_id>/upload',methods=['POST'])(self.media_upload)
        self.bp.route('/location-conditions',methods=['GET'])(self.request_current_location_condition)
        self.bp.route("/<trip_id>/coordinates",methods =["POST"])(self.add_coordinates)
        self.bp.route("/<trip_id>/coordinates",methods =["GET"])(self.get_trip_coors)
        self.bp.route('/<trip_id>/medias',methods =['GET'])(self.get_trip_medias)

    
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
        
        # user data from token
        user_data = self.token_service.decode_jwt(token=token)
        user_id = user_data['user_id']
        # check if user own the trip 
        owner_validation = self.trip_data_base_service.trip_owner_validation(user_id=user_id,trip_id=trip_id)
        if not owner_validation:
            return jsonify({'code':'not authorize', 'message':'Your account are not authorize to modified this trip'}),401
        # get the request data
        data =request.json
        coordinates = data.get("coordinates")
        client_version = data.get('version')
        # data_from_jwt = self.token_service.decode_jwt(token=token)
        # user_id = data_from_jwt['user_id']

        insert, db_version = self.trip_contents_service.insert_coordinates_to_db(trip_id=trip_id,client_version=client_version,coordinates=coordinates)
        print(insert,db_version)
       
       
        if not insert:
            if db_version :
                return jsonify({"code":"missing_versions","message":f"Current version: {db_version} make sure to have the version that higher than this!",'missing_versions':db_version}),409
            return jsonify({"code": "failed", "message":"Failed to save to database"}),500

            

        return jsonify({"code": "successfully", "message":"Successfully store into database"}),200
       
    def media_upload(self,trip_id):
        user_data, error = self._get_authenticated_user()
        user_id = user_data['user_id']
        validation = self.trip_data_base_service.trip_owner_validation(user_id=user_id,trip_id=trip_id)
        if not validation:
            return jsonify({'code':'not authorize', 'message':'Your account are not authorize to modified this trip'}),401
        data = json.loads(request.form.get('data'))
        longitude = data.get('longitude')
        latitude = data.get('latitude')
        time = data.get('time_stamp')  
        image = request.files.get('image')
        upload_status =None
        db_version =None
        if image:
            path = image.filename
            image_version = data.get('version')

            upload_status,db_version = self.trip_contents_service.upload_media('image',path=path,media=image,longitude=longitude,latitude=latitude, trip_id=int(trip_id),client_version=int(image_version),time=time)
        else:
            video = request.files.get('video')
            video_path = video.filename
            video_version = data.get('video_version')
            upload_status,db_version = self.trip_contents_service.upload_media('video',path=video_path,media=video,longitude=longitude,latitude=latitude, trip_id=int(trip_id),client_version=int(video_version),time=time)
            
            
        
        print(upload_status,db_version)
        if not upload_status:
            
            if db_version:
                return jsonify({'message':'Missing verison','missing_versions':db_version}),409
            return jsonify({'message':'Failed!'}),500
        
        return jsonify({'message':'Successfully'}),200
    
    def request_current_location_condition(self):
        user_data, error = self._get_authenticated_user()
        # return if jwt in valid or expried
        if error:
            return (error),401
        user_id = user_data['user_id']
        longitude = request.args.get('longitude',type=float)
        latitude = request.args.get('latitude',type = float)
        geo_data = None
        city = None
        if longitude and latitude:
            geo_data = self.geo_service.get_geo_data(longitude=longitude,latitude=latitude)
            return jsonify({'message':'Successfully!','geo_data':geo_data}),200    
    
    def get_trip_coors (self,trip_id:int):
        user_data, error = self._get_authenticated_user()
        if error:
            return jsonify(error),401
        client_version = smart_cast(request.headers.get('version'))
        coors, version= self.trip_contents_service.get_trip_coors(client_version=client_version,trip_id=trip_id)
        belong_to =self.trip_contents_service.get_trip_belong_to(trip_id=trip_id)
        if not coors and not version:
            return jsonify({'message':'match'}),304
        if not coors :
            return jsonify ({'message':'Failed'}),500
        
        return jsonify({'message':"Successfully",'coordinates':coors,'user_id':belong_to,'newest_version':version}),200
    
    
    def get_trip_medias (self,trip_id:int):
        user_data,error = self._get_authenticated_user()
        if error:
            return jsonify(error),401
        client_version = smart_cast(request.headers.get('Version'))
        medias,version = self.trip_contents_service.get_trip_media(trip_id=trip_id,client_version=client_version)
        if not medias and not version:
            return jsonify({'message':"Match"}),304

        
        return jsonify({'message':"Successfully",'medias':medias}),200
    