## the purpose is to let the main server trigger the events server, make the events server notify the user

from src.notification.push_notification_payload import PushNotificationPayload
from src.error_handler.error_handler import ErrorHandler
import redis
import os
import json
import requests
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)

from requests.exceptions import ConnectionError, HTTPError

def GENERATE_SINGLE_ROOM(user_id:int):
    return f'user:{user_id}'

ALLOW_EVENT_TYPES = ['friend_request','friend_removed','friend_added','friend_reject','friend_cancel','friend_accept']
class NotififcationService:
    _instance = None
    _init = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init:
            return

        self.redis =redis.Redis(
            host=os.environ.get("REDIS_HOST"),
            port=os.environ.get("REDIS_PORT"),
            decode_responses=True,
        )
        self.ErrorService = ErrorHandler().logger('notification')
        self.session = requests.Session()
        # self.session.headers.update(
        #     {
        #         "Authorization": f"Bearer {os.getenv('EXPO_TOKEN')}",
        #         "accept": "application/json",
        #         "accept-encoding": "gzip, deflate",
        #         "content-type": "application/json",
        #     }
        # )
        self._init = True

    def notify(self,room_id:str,event_type:str,data:any):
        try:
            if event_type not in ALLOW_EVENT_TYPES:return False
            self.redis.publish('notifications', json.dumps({'room_id':room_id,'data':data,'event_type':event_type}))
            return True
        except Exception as e:
            print(e)
            self.ErrorService.error(str(e))
            return False

    def push_notify(self,payload:PushNotificationPayload | list[PushNotificationPayload]):

        try:
            response = requests.post(
                "https://exp.host/--/api/v2/push/send",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            # log the error
            print(f"Failed to send notification: {e}")
            self.ErrorService.error(f'failed to send push notification',str(e))

        print(response.json())
        return response
