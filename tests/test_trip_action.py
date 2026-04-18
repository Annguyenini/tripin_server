import pytest
import json
import datetime
from urllib3 import encode_multipart_formdata
@pytest.fixture(scope='session')
def test_create_trip(get_header,client,get_auth,get_test_trip_name):
   
    res = client.post('/trip/request-new-trip',headers =get_header,data ={'trip_name':get_test_trip_name})
    print(res.get_json())
    assert res.status_code == 200
    return res.get_json()
COORDINATE_OBJECT ={
    "coordinates":[
    {
    "time_stamp":1776378591548,
    "latitude": 111.11,
    "longitude": 111.11,
    "altitude": 111.11,
    "speed": 111.11,
    "heading": 111.11,
    "coordinate_id":"63057dd7-1111-1111-1111-5c3009dc3dfb",
    'event':'add',
    'modified_time':1776378591548
    },
    {
    "time_stamp":1776378591548,
    "latitude": 111.11,
    "longitude": 111.11,
    "altitude": 111.11,
    "speed": 111.11,
    "heading": 111.11,
    "coordinate_id":"63057dd7-2222-1111-1111-5c3009dc3dfb",
    "event":'add',
    'modified_time':1776378591548
    }
],
}
def _get_image_data_content_type(trip_id:int)->tuple[bytes|str]:
    image_path = f'trip_{trip_id}_111122223333.png'
    with open('tests/medias/icon.png','rb') as f:
        file_byte = f.read()
    image_formdata ={'image':(
        image_path,
        file_byte,
        'image/png'
    ),
    'data':json.dumps({
        'trip_id': 11,
        'longitude': 11,
        'latitude': 11,
        'time_stamp': 11,
        'media_id': 11,
        'coordinate_id': '63057dd7-1111-1111-1111-5c3009dc3dfb'
    })}
    body,content_type = encode_multipart_formdata(image_formdata)
    print(content_type,body[-500:])
    return body,content_type
def _get_video_data_content_type(trip_id:int)->tuple[bytes|str]:
    video_path = f'trip_{trip_id}_111122333.mp4'
    with open ('tests/medias/video.mp4','rb')as f:    
        file_byte=f.read()
    video_formdata ={
        'video':(
        video_path,
        file_byte,
        'video/mp4'
    ),
    'data':json.dumps({
        'trip_id': 11,
        'longitude': 11,
        'latitude': 11,
        'time_stamp': 11,
        'media_id': 11,
        'coordinate_id': '63057dd7-2222-1111-1111-5c3009dc3dfb'
    })}
    body,content_type = encode_multipart_formdata(video_formdata)
    return body,content_type

def test_modify_trip_detail(client,test_create_trip,get_header):
    new_trip_name= 'test11'
    trip_id = test_create_trip['trip_id']
    data = {
        'trip_id': trip_id,
        'trip_name':new_trip_name
    }
    modify=client.post('/trip/modify-trip-data',headers=get_header,data=data)
    print(modify.get_json())
    # assert modify.status_code==200
    pass


def test_content_flow(get_header,test_create_trip,client,get_auth,get_test_trip_name):
    # create trip 
    trip_id = test_create_trip['trip_id']
    assert trip_id
    # add coodinate 
    send_coordinate = client.post(f'/trip-contents/{trip_id}/coordinates',headers=get_header,json=COORDINATE_OBJECT)
    print(send_coordinate.get_json())
    assert send_coordinate.status_code == 200
    # upload media
   
    image_body,image_content_type = _get_image_data_content_type(trip_id=trip_id)
    send_image = client.post(f'/trip-contents/{trip_id}/upload',headers ={**get_header,'Content-Type':image_content_type},data =image_body)
    print(send_image.get_json())

    assert send_image.status_code ==200
    
    video_body,video_content_type =_get_video_data_content_type(trip_id=trip_id)
    send_medias = client.post(f'/trip-contents/{trip_id}/upload',headers ={**get_header,'Content-Type':video_content_type},data =video_body)
    print(send_medias.get_json())
    assert send_medias.status_code ==200    
    pass

# def test_get_trip_content(get_header,test_create_trip,client,get_auth,get_test_trip_name):
#     response = set()
    
#     trip_id = test_create_trip['trip_id']
#     coordinate = client.get(f'/trip-contents/{trip_id}/coordinates',headers = get_header)
#     assert coordinate.status_code ==200
#     media = client.get(f'/trip-contents/{trip_id}/medias',headers = get_header)
#     assert media.status_code ==200
#     for coor in coordinate.get_json()['coordinates']:
#         response.add(coor.coordinate_id)
    
#     for media in media.get_json()['medias']:
#         response.add(coor.media_id)

#     for coord in COORDINATE_OBJECT['coordinates']:
#         assert coord.coordinate_id in response 
#     pass

def test_create_trip_while_active(client,get_header,get_test_trip_name):
    res = client.post('/trip/request-new-trip',headers =get_header,json={'trip_name':f'{get_test_trip_name}'})
    assert res.status_code == 500


def test_end_trip(client,test_create_trip,get_header):
    trip_id = test_create_trip['trip_id']
    end = client.post('/trip/end-trip',headers = get_header, json ={'trip_id':trip_id})
    assert end.status_code ==200
def test_create_trip_duplicate_name():
    pass