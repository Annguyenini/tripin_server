import requests
import dotenv
import os
from datetime import datetime
import time
import threading
dotenv.load_dotenv()
DISCORD_ERROR_WEBHOOK = os.getenv('DISCORD_ERROR_WEBHOOK',None)
DISCORD_REQUEST_WEBHOOK =os.getenv('DISCORD_REQUEST_WEBHOOK',None)
DISCORD_STATUS_WEBHOOK = os.getenv('DISCORD_STATUS_WEBHOOK',None)
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
        
def discord_server_status_logs(message,color):
    if DISCORD_STATUS_WEBHOOK:
        data ={ "embeds": [
                {   
                    "title": "Request",
                    "description": message,
                    "color": color  # this is a hex integer
                }
            ]}
        requests.post(DISCORD_STATUS_WEBHOOK,json=data)
        
        
def start_server_status_thread():
    if not DISCORD_STATUS_WEBHOOK: return
    threading.Thread(target=server_satus_log,daemon=True).start()

def server_satus_log(url="http://127.0.0.1:8000/health"):
    TIME = 60 
    WAS_DOWN = True
    COLOR_RED = 0xFF0000
    COLOR_GREEN = 0x00FF00
    while True:
        try:
            res = requests.get(url,timeout=5)
            print(res)
            if res.status_code ==200:
                if WAS_DOWN:
                    discord_server_status_logs("🟢 Server BACK UP \n{url} is back online!", COLOR_GREEN)
                    WAS_DOWN = False
            elif res.status_code !=200:
                if not WAS_DOWN:
                    discord_server_status_logs("🔴 Server DOWN \n{url} returned {res.status_code}", COLOR_RED)
                    WAS_DOWN = True
        except Exception as e:
            if not WAS_DOWN:
                discord_server_status_logs("🔴 Server DOWN \ncould not reach {url}", COLOR_RED)
                WAS_DOWN = True
        time.sleep(TIME)