from werkzeug.http import generate_etag
from src.server_config.service.cache import Cache
from src.database.database import Database
import json
class EtagService:
    _instance = None
    _init = False
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.cacheService = Cache()
        self.databaseService = Database()
        
        
    def generate_Etag_from_object(self,data):
        encoded_data =json.dumps(data,sort_keys=True).encode('utf-8')
        etag = generate_etag(encoded_data, weak=False)
        return etag

    def generate_etag(self,key):
        etag = generate_etag(key.encode('utf-8'))
        strong_etag = etag.strip('W/')
        return strong_etag

  