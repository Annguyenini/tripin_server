
def test_login_valid_credential(client,user_credential):
    payload ={
        'username':user_credential['username'],
        'password':user_credential['password']
    }
    response = client.post("auth/login",json=payload)
    print(response.get_json())
    assert response.status_code == 200 
    assert 'tokens' in response.get_json()

def test_login_invalid_credential(client,user_credential):
    payload = {
        "username" :user_credential['invalid_username'],
        "password" :user_credential['invalid_password']
    }
    response = client.post("auth/login",json=payload)
    assert response.status_code == 401 
    
