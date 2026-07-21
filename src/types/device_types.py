from dataclasses import dataclass
from datetime import datetime

@dataclass
class Device:
    user_id:int
    device_id:str
    token:str
    platform:str
    last_seen:int

@dataclass
class DatabaseDevice:
    user_id:int
    device_id:str
    token:str
    platform:str
    last_seen:datetime
