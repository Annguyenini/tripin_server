import requests 
def test_login_valid_credential():
    payload = {
        "username" :"Annguyen",
        "password" :"Annguyen2005@"
    }
    response = requests.post("http://127.0.0.1:8000/auth/login",json=payload)
    assert response.status_code == 200 ,"Successfully"
    data = response.json()

test_login_valid_credential()
