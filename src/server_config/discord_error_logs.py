import requests
import dotenv
import os
from datetime import datetime


dotenv.load_dotenv()
DISCORD_ERROR_WEBHOOK = os.getenv('DISCORD_ERROR_WEBHOOK',None)
DISCORD_REQUEST_WEBHOOK =os.getenv('DISCORD_REQUEST_WEBHOOK',None)
def discord_error_logs(message):
    color =0xFF0000
    if DISCORD_ERROR_WEBHOOK:
        data ={ "embeds": [
            {
                "title": "🚨 Flask Error",
                "description": message,
                "color": color  # this is a hex integer
            }
        ]}
        requests.post(DISCORD_ERROR_WEBHOOK,json=data)
def discord_request_logs(message,code):
    if DISCORD_REQUEST_WEBHOOK:
        if code // 100 == 2:
            color = 0x00FF00
        elif code // 100 == 3:
            color = 0x0000FF
        elif code //100 == 4:
            color = 0xFF0000
        else:
            color = 0xFF0000
            
        data ={ "embeds": [
            {   
                "title": "Request",
                "description": message,
                "color": color  # this is a hex integer
            }
        ]}
        requests.post(DISCORD_REQUEST_WEBHOOK,json=data)