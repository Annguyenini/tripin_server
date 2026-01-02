from src.server_config.service.Etag.Etag import EtagService

class TripDataEtag (EtagService):
    _instance = None
    _init = False
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls=cls)
        return cls._instance
    
    def __init__(self):
        if self._init:return
        super()
        self._init = True
        
    def generate_etag_handler(self,key:str,trip_object):
        try:
            etag = self.generate_Etag_from_object(trip_object)
            self.cacheService.set(key=key,time=3600,data=etag)
        except Exception as e:
            print(e)
        return 
    
    def set_etag_to_cache(self,key,etag):
        try:
            self.cacheService.set(key=key,time=3600,data=etag)
        except Exception as e :
            print(e)
        
        return
    
    def get_etag_from_cache(self,key:str):
        try:
            etag = self.cacheService.get(key=key)
            return etag
        except Exception as e:
            print(e)
        return None