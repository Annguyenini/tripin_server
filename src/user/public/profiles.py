# this service use to get other user data service, limit what data will be return
from src.database.s3.s3_service import S3Sevice
from src.repository.user_data_repository import UserDataRepository
from src.utils.handle_exception import handle_exception
from src.utils.cache.cache import Cache
from src.utils.cache.keys.cache_keys import GetProfileCacheKey, GetUserDataCacheKey
import json
class ProfilesService :
    _instace = None
    _init = False

    def __new__(cls):
        if cls._instace is None:
            cls._instace = super().__new__(cls)
        return cls._instace

    def __init__(self):
        if self._init:
            return
        self.UserDataRepository = UserDataRepository()
        self.S3Service = S3Sevice()
        self.Cache = Cache()

        self._init = True

    @handle_exception('Public User Data','get-user-data')
    def get_user_data(self,target_user_id:int):
        # seem like we will take the trade off, we will not cache this, since user repository, and temp url already cache
        # we will trade cache to make it easier to maintain
        #
        # cache_key = GetProfileCacheKey(user_id=target_user_id)
        # raw_cache_data = self.Cache.get(key=cache_key)
        # if raw_cache_data:
        #     cache_data = json.loads(raw_cache_data)
        #     return {'code':'successfully','message':'successfully','user_data':cache_data},200
        user_data = self.UserDataRepository.get_user_data(target_user_id)
        if user_data is None:
            return {'code':'empty','message':'Empty'},200
        if user_data['avatar']:
            user_data['avatar']=S3Sevice.generate_temp_uri(key=user_data['avatar'])
        public_data  = {
            'user_id':user_data.get('id'),
            'display_name':user_data.get('display_name'),
            'user_name':user_data.get('user_name'),
            'avatar':user_data.get('avatar')}
        # self.Cache.set(key=cache_key,data=json.dumps(public_data),time=3600)
        return {'code':'successfully','message':'successfully','user_data':public_data},200

    @handle_exception('Public User Data','search-for-user')

    def search_for_user(self,keywords:str):
        if not keywords or len(keywords) <3:
            raise ValueError('Invalid Keywords')
        users = self.UserDataRepository.search_user(keywords=keywords)
        return {'users':users},200
        pass
