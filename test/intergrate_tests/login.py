import requests
def login_flow():

    header = {'Content-Type':'application/json'}
    payload = {
        'username':'Annguyen',
        'password':'Annguyen2005@'
    }
    
    respond =requests.post(url='http://127.0.0.1:8000/auth/login',json = payload)
    data = respond.json()
    print(respond.json())
    user_data = data['user_data']
    user_id = user_data['user_id']
    tokens = data['tokens']
    access_token = tokens['access_token']
    current_trip_header ={
        'Authorization':f'Bearer {access_token}'
    }
    current_trip_payload = {
        'user_id':user_id
    }
    # current_trip_respond = requests.get(url='http://127.0.0.1:8000/trip/current-trip',headers= current_trip_header,json=current_trip_payload)
    # current_trip_id = current_trip_respond.json()['current_trip_id']
    
    # trip_respond = requests.get(url=f'http://127.0.0.1:8000/trip/trip/{current_trip_id}',headers=current_trip_header)
    # etag = trip_respond.json()['etag']
    
    # second_current_trip_header={
    #     'Authorization':f'Bearer {access_token}',
    #     'If-Not-Match':f'{etag}'
    # }
    # second_current_trip_respond = requests.get(url=f'http://127.0.0.1:8000/trip/trip/{current_trip_id}',headers= second_current_trip_header)
    # all_trip_respond = requests.get(url='http://127.0.0.1:8000/trip/trips',headers= current_trip_header)
    # etag = all_trip_respond.json()['etag']
    second_current_trip_header={
        'Authorization':f'Bearer {access_token}',
        'If-Not-Match':'63925a9d3393f8fc81de9503319f6c5e0e5f855d'
    }
    second_all_trip_respond = requests.get(url='http://127.0.0.1:8000/trip/trips',headers= second_current_trip_header)
    print(second_all_trip_respond.status_code)
    
login_flow()