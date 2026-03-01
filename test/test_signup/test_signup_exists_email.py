import requests
def test_signup_exist_email():
    payload = {
        "email" :"test@gmail.com",
        "displayName" : "",
        "username" :"",
        "password" :"@"
    }
    response = requests.post("http://127.0.0.1:8000/auth/signup",json=payload)
    assert response.status_code == 401 ,"User exist email still throught"
    data = response.json()
    print("Exist email signup case: ",data)
test_signup_exist_email()