import requests
def test_login_with_token():
    token =""
    assert token.strip() != "", "Invalid token"
    headers ={
        "Authorization":f"Bearer {token}"
    }
    response = requests.post("https://127.0.0.1:8000/auth/login-via-token",headers=headers)
    data  = response.json()
    print(data)
    assert response.status_code ==200, "Unsuccessfully"
    assert data['userdatas']['user_id']==1,"wrong user id"
    assert data['userdatas']["user_name"]=="Annguyen","wrong user name"
    assert data['userdatas']["display_name"]=="Annguyen","wrong display"
    
test_login_with_token()