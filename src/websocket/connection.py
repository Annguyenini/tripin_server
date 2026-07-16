import json
import os
import threading

import redis
from flask import Blueprint, jsonify, request
from flask_socketio import SocketIO, join_room

from src.base.route_base import RouteBase
from src.token.tokenservice import TokenService


class Socket:
<<<<<<< HEAD
    _instance = None
    _init = False

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
=======
    _init = False

>>>>>>> c352977 (socket io)

    def __init__(self, app):
        if self._init:
            return
        self.socketIO = SocketIO(
<<<<<<< HEAD
            app, cors_allowed_origins="*", message_queue=os.environ.get("REDIS_URL")
=======
            app, cors_allowed_origins="*", message_queue=os.environ.get("REDIS_URL"),        async_mode="threading"


>>>>>>> c352977 (socket io)
        )
        self.TokenService = TokenService()
        self.register_events()
        self._init = True

    def register_events(self):

        # see accesstoken shape
        @self.socketIO.on("connect")
        def connect(auth):
            access_token = auth.get("access_token")
            if not access_token:
                return False
<<<<<<< HEAD
            user_data = self.TokenService.decode_jwt(token=access_token)
            user_id = user_data.get("user_id")
=======
            user_data = self.TokenService.decode_jwt(token=access_token,fields=['user_id'])
            user_id = user_data.get("user_id")
            # user_id = '1'
>>>>>>> c352977 (socket io)
            # string
            room_id = f"user:{user_id}"
            join_room(room=room_id)

        @self.socketIO.on("disconnect")
        def disconnect():
            print("client disconnect")
<<<<<<< HEAD

=======
        @self.socketIO.on("message")
        def handle_message(data):
            print("Received from client:", data)

            # send response back
            self.socketIO.emit(
                "message_response",
                {
                    "status": "received"
                },
            )
>>>>>>> c352977 (socket io)

## we can use mem to do this instead on redis, but in the future we could have 2 server running in parrallel, so make redis as central
class NotificationRedisPubSub:
    def __init__(self, socketIO) -> None:
        self.redis = redis.Redis(
            host=os.environ.get("REDIS_HOST"),
            port=os.environ.get("REDIS_PORT"),
            decode_responses=True,
        )
        self.socket = socketIO

    ## listener for notifications

    def redis_listener(self):
        pubsub = self.redis.pubsub()
        pubsub.subscribe("notifications")
        for message in pubsub.listen():
            if message["type"] != "message":
                continue
            data = json.loads(message["data"])
            room_id = str(data["room_id"])
            self.socket.socketIO.emit("notifications", data, to=room_id)

    def start_listener_thread(self):
        thread = threading.Thread(target=self.redis_listener, daemon=True)
        thread.start()
