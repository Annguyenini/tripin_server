from dataclasses import dataclass
from datetime import datetime

@dataclass
class Device:
    user_id:int
    device_id:str
    platform:str
    last_seen:int
    push_token:str | None = None

@dataclass
class DatabaseDevice:
    user_id:int
    device_id:str
    platform:str
    last_seen:datetime
    push_token:str | None = None
