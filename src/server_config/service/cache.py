import os

import dotenv
from flask import Flask
from redis import Redis


class Cache:
    _instance = None
    _init = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        if self._init:
            return
        dotenv.load_dotenv("src/assets/configs/.env")
        host = os.getenv("REDIS_HOST")
        port = os.getenv("REDIS_PORT")
        self.redis_client = Redis(host=host, port=int(port), decode_responses=True)
        _init = True

    def get_redis_client(self) -> Redis:
        if not self.redis_client:
            self.__init__()
        return self.redis_client

    def incr(self, key):
        return self.redis_client.incr(key)

    def exp(self, key, seconds):
        self.redis_client.expire(key, seconds)

    def get(self, key: str) -> str:
        return self.redis_client.get(key)

    def set(self, key, time, data):
        try:
            self.redis_client.setex(key, time, data)
            return True
        except Exception as e:
            return False

    def touch(self, key: str, time: int) -> None:
        try:
            self.redis_client.expire(key, time)
        except Exception as e:
            print(e)

    def delete(self, key):
        self.redis_client.delete(key)

    def close(self):
        self.redis_client.close()
