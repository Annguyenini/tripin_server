from flask import Flask
from redis import Redis 

class RateLimiterRedis:
    _instance =None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.redis_client = Redis (host ="localhost", port =6379, decode_responses =True )
    
    
    def incr (self,key):
        return self.redis_client.incr(key)
        
    def exp (self,key,seconds):
        self.redis_client.expire(key,seconds)
        
    def get (self,key):
        return self.redis_client.get(key)
    
    def close(self):
        self.redis_client.close()

