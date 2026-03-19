from flask import jsonify,Blueprint,request
from src.token.tokenservice import TokenService
from src.trip_service.trip_contents.trip_contents_service import TripContentService
from src.geo.geo_service import GeoService
from src.server_config.service.smart_cast import smart_cast
from src.database.trip_db_service import TripDatabaseService
from src.database.trip_content_db_service  import TripContentsDatabaseService
from src.base.route_base import RouteBase
from src.server_config.service.Etag.trip_etag_service import TripEtagService
from src.error_code.error_code import ERROR_KEYS,ERROR_MESSAGE
import json
import time
from src.error_code.error_code import ERROR_KEYS ,ERROR_MESSAGE
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
        self.trip_etag_service =TripEtagService()
        self._register_route()
        self._init =True

    def _register_route(self):
        # POST   /<trip_id>/upload              — upload photo or video to a trip
        # GET    /location-conditions           — get geo data for current coordinates
        # POST   /<trip_id>/coordinates         — add new coordinates to a trip
        # GET    /<trip_id>/coordinates         — get coordinates for owned trip (JWT)
        # GET    /<token>/coordinates-by-token  — get coordinates via public share token
        # GET    /<token>/medias-by-token       — get media via public share token
        # GET    /<trip_id>/medias              — get media for owned trip (JWT)
        self.bp.route ('/<trip_id>/upload',methods=['POST'])(self.media_upload)
        self.bp.route('/location-conditions',methods=['GET'])(self.request_current_location_condition)
        self.bp.route("/<trip_id>/coordinates",methods =["POST"])(self.add_coordinates)
        self.bp.route("/<trip_id>/coordinates",methods =["GET"])(self.get_trip_coors)
        self.bp.route("/<token>/coordinates-by-token",methods =["GET"])(self.get_trip_coors_by_token)
        self.bp.route("/<token>/medias-by-token",methods =["GET"])(self.get_trip_medias_by_token)
        self.bp.route('/<trip_id>/medias',methods =['GET'])(self.get_trip_medias)
        self.bp.route('/delete-media',methods=["DELETE"])(self.delete_media)   
        self.bp.route('/trip-medias-hash',methods=['POST'])(self.get_trip_medias_hash)
        self.bp.route('/trip-medias-metadata',methods=['POST'])(self.get_trip_media_metadata)
    def add_coordinates(self,trip_id):
        """Add a batch of coordinates to a trip.
        Requires JWT auth and trip ownership.
        Validates client version to prevent out-of-order writes.
        """
        user_data, error = self._get_authenticated_user()
        if error:
            return (error),401
        
        user_id = user_data['user_id']

        # check if user owns the trip 
        owner_validation = self.trip_data_base_service.trip_owner_validation(user_id=user_id,trip_id=trip_id)
        if not owner_validation:
            return jsonify({'code':'not authorize', 'message':'Your account are not authorize to modified this trip'}),401

        # extract coordinates and client version from request body
        data =request.json
        coordinates = data.get("coordinates")
        client_version = data.get('version')

        # attempt to insert — returns (success, db_version)
        insert, db_version = self.trip_contents_service.insert_coordinates_to_db(trip_id=trip_id,client_version=client_version,coordinates=coordinates)
        print(insert,db_version)
       
        if not insert:
            # version conflict — client is behind, return current db version
            if db_version :
                return jsonify({"code":"missing_versions","message":f"Current version: {db_version} make sure to have the version that higher than this!",'missing_versions':db_version}),409
            return jsonify({"code": "failed", "message":"Failed to save to database"}),500

        return jsonify({"code": "successfully", "message":"Successfully store into database"}),200
       
    def media_upload(self,trip_id):
        """Upload a photo or video to a trip.
        Requires JWT auth and trip ownership.
        Accepts multipart form with 'image' or 'video' file + metadata JSON in 'data' field.
        """
        user_data, error = self._get_authenticated_user()
        if error:
            return (error),401
        user_id = user_data['user_id']

        # check trip ownership
        validation = self.trip_data_base_service.trip_owner_validation(user_id=user_id,trip_id=trip_id)
        if not validation:
            return jsonify({'code':'not authorize', 'message':'Your account are not authorize to modified this trip'}),403
        try:
            # parse metadata from multipart form
            data = json.loads(request.form.get('data'))
        except (json.JSONDecodeError, TypeError):
            return jsonify({'message': 'Invalid metadata'}), 400
        longitude = data.get('longitude')
        latitude = data.get('latitude')
        time = data.get('time_stamp')  

        image = request.files.get('image') 
        upload_status =None
        media_id = data.get('media_id')  
        if image:
            # handle image upload
            path = image.filename
            upload_status,hash = self.trip_contents_service.upload_media('image',path=path,media=image,longitude=longitude,latitude=latitude, trip_id=int(trip_id),time=time,media_id=media_id)
        else:
            # handle video upload
            video = request.files.get('video')
            video_path = video.filename
            upload_status,hash = self.trip_contents_service.upload_media('video',path=video_path,media=video,longitude=longitude,latitude=latitude, trip_id=int(trip_id),time=time,media_id=media_id)
            
        if not upload_status:
            return jsonify({'code':ERROR_KEYS.FAILED,'message':ERROR_MESSAGE.SERVER_FAILED}),500
        return jsonify({'message':'Successfully','hash':hash}),200
    
    def delete_media(self):
        user_data, error =self._get_authenticated_user()
        if error:
            return (error),401
        user_id = user_data['user_id']
        trip_data = request.json
        # get media path, if none return
        media_id = trip_data['media_id']
        if not media_id : return ({'code':'no_media_id','message':'No media_id or invalid value type was send!'})

        
        trip_id=smart_cast(trip_data['trip_id'])
        #check for permission
        owner_validation = self.trip_data_base_service.trip_owner_validation(user_id=user_id,trip_id=trip_id)
        if not owner_validation:
            return jsonify({'code':'not authorize', 'message':'Your account are not authorize to modified this trip'}),401
        # pocess delete
        delete_media, error_delete = self.trip_contents_service.delete_media(media_id=media_id,trip_id=trip_id)
        if not delete_media:
            return (error_delete),500
        hash = self.trip_contents_service.get_trip_medias_hash(trip_id=trip_id)
        return({'code':'successfully','message':'Media delete from server successfully!','hash':hash}),200
    
    def request_current_location_condition(self):
        """Get geo/weather conditions for a given lng/lat.
        Requires JWT auth.
        Query params: longitude, latitude (floats)
        """
        user_data, error = self._get_authenticated_user()
        # return if jwt is invalid or expired
        if error:
            return (error),401
        user_id = user_data['user_id']

        # read coordinates from query params
        longitude = request.args.get('longitude',type=float)
        latitude = request.args.get('latitude',type = float)
        geo_data = None
        city = None

        if longitude and latitude:
            geo_data = self.geo_service.get_geo_data(longitude=longitude,latitude=latitude)
            return jsonify({'message':'Successfully!','geo_data':geo_data}),200    
    
    def get_trip_coors(self,trip_id:int):
        """Get all coordinates for a trip. JWT + ownership required.
        Supports ETag-style caching via 'version' request header.
        Returns 304 if client version matches, 200 with data otherwise.
        """
        # token validation 
        user_data, error = self._get_authenticated_user()
        if error:
            return jsonify(error),401

        # check for authorization 
        user_id = user_data['user_id']
        authorize = self.trip_data_base_service.trip_owner_validation(user_id=user_id,trip_id=trip_id)
        if not authorize:
            return jsonify({'code':'not authorize','message':'You are not authorize to get this trip data!'})

        # get client version from header for cache comparison
        client_version = smart_cast(request.headers.get('version'))
        coors, version= self.trip_contents_service.get_trip_coors(client_version=client_version,trip_id=trip_id)
        belong_to =self.trip_contents_service.get_trip_belong_to(trip_id=trip_id)

        # cache hit — data unchanged
        if not coors and not version:
            return jsonify({'message':'match'}),304

        if not coors :
            return jsonify ({'message':'Failed'}),500
        
        return jsonify({'message':"Successfully",'coordinates':coors,'user_id':belong_to,'newest_version':version}),200
    
    def get_trip_coors_by_token(self,token):
        """Get coordinates for a trip via public share token (no JWT needed).
        Supports HTTP ETag caching via If-None-Match header.
        Returns 304 if data unchanged, 200 with coordinates otherwise.
        """
        # validate token format — must be 64 char sha256 hex
        if not token or len(token) != 64:
            return jsonify({'code': 'invalid_token', 'message': 'Invalid token'})

        # resolve token → trip_id from share_links table
        trip_data = self.trip_data_base_service.get_trip_data_by_shared_token(token=token)
        trip_id = trip_data['trip_id']
        #check for etag if it match the time frame
        client_etag = request.headers.get('If-None-Match')
        etag =None
        etag_key = self.trip_etag_service.get_trip_coordinate_etag_key(trip_id)
        etag= self.trip_etag_service.generate_etag(etag_key)
        
        if client_etag == etag:
            return jsonify({'message':"Match"}),304
        # if not match
        coors, version= self.trip_contents_service.get_trip_coors(client_version=0,trip_id=trip_id)

        # cache hit — data unchanged
        if not coors and not version:
            return jsonify({'message':'match'}),304

        if not coors :
            return jsonify ({'code':'failed','message':'Failed to get coordinates'}),500
        
        # attach ETag to response so browser can cache it
        response = jsonify ({'coordinates':coors})
        if version:
            response.headers['ETag'] = etag
        return response,200
        
        
    def get_trip_medias(self,trip_id:int):
        """Get all media (photos/videos) for a trip. JWT + ownership required.
        Supports version-based caching via 'Version' header.
        Returns 304 if client version matches, 200 with media list otherwise.
        """
        user_data,error = self._get_authenticated_user()
        if error:
            return jsonify(error),401

        # check for authorization 
        user_id = user_data['user_id']
        authorize = self.trip_data_base_service.trip_owner_validation(user_id=user_id,trip_id=trip_id)
        if not authorize:
            return jsonify({'code':'not_authorize','message':'You are not authorize to get this trip data!'}),403
        
        client_hash = request.headers.get('If-None-Match')
        server_hash = self.trip_contents_service.get_trip_medias_hash(trip_id=trip_id)\
        
        # return if both have same contents
        if client_hash==server_hash:
            return jsonify({'message':"Match"}),304
        
        # get client version for cache comparison
        medias = self.trip_contents_service.get_trip_media(trip_id=trip_id)

        return jsonify({'message':"Successfully",'medias':medias}),200
    
    def get_trip_medias_by_token(self,token):
        """Get media for a trip via public share token (no JWT needed).
        Supports HTTP ETag caching via If-None-Match header.
        Returns 304 if data unchanged, 200 with media list otherwise.
        """
        # validate token format — must be 64 char sha256 hex
        if not token or len(token) != 64:
            return jsonify({'code': 'invalid_token', 'message': 'Invalid token'})

       
        # resolve token → trip_id from share_links table
        trip_data = self.trip_data_base_service.get_trip_data_by_shared_token(token=token)
        trip_id = trip_data['trip_id']
        #check for etag if it match the time frame
        # due to link of image only valid 1 hour
        client_etag = None
        etag =None
        hour_bucket = int(time.time()) // 3600
        etag_key = self.trip_etag_service.get_trip_medias_etag_key(trip_id,hour_bucket)
        etag= self.trip_etag_service.generate_etag(etag_key)
        
        if client_etag == etag:
            return jsonify({'message':"Match"}),304
        # if not match
        medias,version = self.trip_contents_service.get_trip_media(trip_id=trip_id,client_version=0)

        # cache hit — data unchanged
        if not medias and not version:
            return jsonify({'message':"Match"}),304

        if not medias :
            return jsonify ({'code':'failed','message':'Failed to get medias'}),500


        # attach ETag to response so browser can cache it
        response = jsonify ({'medias':medias})
        if version:
            response.headers['ETag'] = etag
        return response,200
    
    def get_trip_medias_hash(self):
        
        user_data,error = self._get_authenticated_user()
        if error:
            return (error),401
        user_id = user_data ['user_id']
        trip_id = request.json['trip_id']
        trip_validation =self.trip_data_base_service.trip_owner_validation(user_id=user_id,trip_id=trip_id)
        if not trip_validation:
            return jsonify({'code':ERROR_KEYS.NOPERMISSION,'message':ERROR_MESSAGE.NOPERMISSION}),403
        media_hash = self.trip_contents_service.get_trip_medias_hash(trip_id=trip_id)
        if not media_hash:
            return jsonify({'code':ERROR_KEYS.FAILED,'message':ERROR_KEYS.SERVER_FAILED}) 
        return jsonify({'hash':media_hash,'trip_id':trip_id})
    
    def get_trip_media_metadata(self):
        user_data,error = self._get_authenticated_user()
        if error:
            return (error),401
        user_id = user_data ['user_id']
        trip_id = request.json['trip_id']
        trip_validation =self.trip_data_base_service.trip_owner_validation(user_id=user_id,trip_id=trip_id)
        if not trip_validation:
            return jsonify({'code':ERROR_KEYS.NOPERMISSION,'message':ERROR_MESSAGE.NOPERMISSION}),403
        metadata = self.trip_contents_service.get_trip_media_metadata(trip_id=trip_id)
        if not metadata:
            return jsonify({'code':ERROR_KEYS.FAILED,'message':ERROR_KEYS.SERVER_FAILED}) 
        return jsonify({'metadata':metadata,'trip_id':trip_id})