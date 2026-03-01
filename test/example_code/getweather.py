import requests
import json
latitude = 21.027764
longitude = 105.834160
url =f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,pm2_5,pm10,carbon_monoxide,nitrogen_dioxide,ozone,sulphur_dioxide&timezone=auto'
respond = requests.get(url=url)
assert respond.status_code ==200,'error'
with open ('test.json','w')as w:
    json.dump(respond.json(),w,indent=2)