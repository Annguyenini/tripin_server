import requests
def test_signup_exist_username():
    payload = {
        "email" :"tesat@gamil.com",
        "displayName" : "",
        "username" :"",
        "password" :"@"
    }
    response = requests.post("http://127.0.0.1:8000/auth/signup",json=payload)
    assert response.status_code == 401 ,"User exist still throught"
    data = response.json()
    print("Exist username signup case: ",data)
test_signup_exist_username()