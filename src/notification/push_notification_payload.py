from dataclasses import dataclass


@dataclass
class PushNotificationPayload:
    token:str
    title:str
    body:str
    sound:str |None = 'default'
    priority:str |None ='high'
    channelId:str |None = "default"
    data: object | None = None
