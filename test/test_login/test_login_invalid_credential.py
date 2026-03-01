import requests
def test_login_invalid_credential():
    payload = {
        "username" :"",
        "password" :""
    }
    response = requests.post("http://127.0.0.1:8000/auth/login",json=payload)
    assert response.status_code == 429 ,"Unsuccessfully"
    data = response.json()

test_login_invalid_credential()