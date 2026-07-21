from dataclasses import dataclass


@dataclass
class PushNotificationPayload:
    to:str
    title:str
    body:str
    data: object | None = None
