import requests
def test_signup_valid_credentials():
    payload = {
        "email" :"@gmail.com",
        "displayName" : "",
        "username" :"",
        "password" :"@"
    }
    response = requests.post("http://72.62.165.221:80/auth/signup",json=payload)
    assert response.status_code == 200 ,response.json()
    data = response.json()
    print("Perfect signup case: ",data)
    
test_signup_valid_credentials()