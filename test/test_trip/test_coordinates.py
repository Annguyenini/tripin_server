import requests 
def test_coordinates():
    payload = {
        "time_stamp":1111,
        "coordinates":{
            "dsdsd":"dsdsds",
            "dsdsdaaa":"aaaa"
        }
    }
    response = requests.post("http://127.0.0.1:8000/trip/coordinates",json=payload)
    assert response.status_code == 200 ,"Successfully"
    data = response.json()

test_coordinates()
