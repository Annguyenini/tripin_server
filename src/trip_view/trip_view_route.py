from flask import Blueprint,request,jsonify,render_template
from src.base.route_base import RouteBase
from src.server_config.service.smart_cast import smart_cast
from src.database.trip_db_service import TripDatabaseService
from src.database.database_keys import DATABASEKEYS
from src.server_config.config import Config
import secrets
import hashlib
from dotenv import load_dotenv
import os
from datetime import datetime,timezone,timedelta
load_dotenv('.env')
MAPTOKEN =os.getenv('MAPBOX_PUBLIC_KEY')
BASE_URL =os.getenv('BASE_URL')
class TripViewRoute(RouteBase):
    _instance =None 
    _init = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance =super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._init: return
        super().__init__()
        self.bp = Blueprint('trip-view',__name__)        
        self._register_routes()
        self.TripDataBaseService = TripDatabaseService()
        self.Config =Config()
        self._init = True
        
    def _register_routes(self):
        self.bp.route('/<token>',methods=['GET'])(self.request_trip_view)
        self.bp.route('/generate-trip-view-link',methods=['POST'])(self.generate_trip_view_link)
    def generate_trip_view_link(self):
        """generate url using trip view

        Returns:
            _type_: _description_
        """
        user_data_jwt, error = self._get_authenticated_user()
        if error:
            return jsonify(error),401
        user_data = request.json
        user_id = user_data_jwt['user_id']
        trip_id = user_data['trip_id']
        expired_days = user_data['expired_days']
        if not smart_cast(trip_id) or not smart_cast(expired_days):
            return jsonify({'code':'invalid_type_input','message': 'invalid type of input make sure it is number'}),401
        if not self.TripDataBaseService.trip_owner_validation(user_id=user_id,trip_id=trip_id):
            return jsonify({'code':'permistion_denied','message': 'Your account doesnt own or have permission to do this acction!'}),401
        token =self._handle_generate_trips_view_link(user_id=user_id,trip_id=trip_id,expired_days={'days':expired_days})
        
        if not token:
            return jsonify({'code':'failed','message':'Failed to generate view url'}),500
        
        full_url = f'{BASE_URL}/trip-view/{token}'
        return jsonify({'code':'successfully','message':'Successfully create url','url':full_url}),200
    
    def _handle_generate_trips_view_link(self,user_id:int,trip_id:int,expired_days:object) -> str :
        ex_date_in_ms = int((datetime.now(timezone.utc) + timedelta(**expired_days)).timestamp())
        current_date_in_ms = int(datetime.now(timezone.utc).timestamp())
        random_part = secrets.token_urlsafe(16)
        raw = f"{trip_id}:{ex_date_in_ms}:{random_part}"
        token =  hashlib.sha256(raw.encode()).hexdigest()
        con,cur =self.TripDataBaseService.connect_db()
        cur.execute(f'''INSERT INTO {DATABASEKEYS.TABLES.TRIP_SHARED_LINKS} (
            {DATABASEKEYS.TRIP_SHARED_LINKS.TOKEN},
            {DATABASEKEYS.TRIP_SHARED_LINKS.USER_ID},
            {DATABASEKEYS.TRIP_SHARED_LINKS.TRIP_ID},
            {DATABASEKEYS.TRIP_SHARED_LINKS.CREATED_TIME},
            {DATABASEKEYS.TRIP_SHARED_LINKS.EXPIRED_TIME}
            ) VALUES (%s,%s,%s,%s,%s)''',(token,user_id,trip_id,current_date_in_ms,ex_date_in_ms))
        con.commit()
        self.TripDataBaseService.close_db(conn=con)
        return token if cur.rowcount>=1 else None
        
    def request_trip_view(self,token):
        trip_data = self._get_data_using_token(token=token)
        if not trip_data:
            
            return render_template('500.html'),500
        # check if the token still valid 
        current_date_in_ms = int(datetime.now(timezone.utc).timestamp())
        if current_date_in_ms > int(trip_data['expired_time']):
            return jsonify ({'code':'url_expired','message':'Url expired!'}),401
        # check if visibility allow
        if trip_data ['visibility'] != 'public':
            return jsonify({'code':'permission denied','message':f'you dont have permission to view this trip, this trip is set as {trip_data ['visibility']}'}),500
        return render_template('trip_view.html',MAPTOKEN=MAPTOKEN,BASE_URL=BASE_URL)
        # if pass we get ready to return template
        
        
    def _get_data_using_token(self,token:str):
        con,cur = self.TripDataBaseService.connect_db()
        cur.execute(f'''SELECT * FROM {DATABASEKEYS.TABLES.TRIP_SHARED_LINKS}
                    WHERE {DATABASEKEYS.TRIP_SHARED_LINKS.TOKEN} = %s''', (token,))
        row = cur.fetchone()
        self.TripDataBaseService.close_db(conn=con)
        return row if row else None