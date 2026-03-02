from flask import Flask
from redis import Redis 
import dotenv
import os
class Cache:
    _instance =None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            
        return cls._instance
    
    def __init__(self):
        dotenv.load_dotenv('src/assets/configs/.env')
        host = os.getenv('REDIS_HOST')
        port =os.getenv('REDIS_PORT')
        self.redis_client = Redis (host =host, port =port, decode_responses =True )

    
    def incr (self,key):
        return self.redis_client.incr(key)
        
    def exp (self,key,seconds):
        self.redis_client.expire(key,seconds)
        
    def get (self,key):
        return self.redis_client.get(key)
    
    def set(self,key,time,data):
        self.redis_client.setex(key,time,data)
    
    def delete(self,key):
        self.redis_client.delete(key)
    
    def close(self):
        self.redis_client.close()

