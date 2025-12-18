import requests
def test_signup_valid_credentials():
    payload = {
        "email" :"abdc@gmail.com",
        "displayName" : "abcd",
        "username" :"abcd",
        "password" :"Abcd22@"
    }
    response = requests.post("http://127.0.0.1:8000/auth/signup",json=payload)
    assert response.status_code == 200 ,"User was created successfully"
    data = response.json()
    print("Perfect signup case: ",data)
    
test_signup_valid_credentials()