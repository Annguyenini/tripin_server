
def test_login_valid_credential(client,user_credential):

    response = client.post("auth/login",json=user_credential)
    assert response.status_code == 200 
    assert 'tokens' in response.get_json()

def test_login_invalid_credential(client):
    payload = {
        "username" :"",
        "password" :""
    }
    response = client.post("auth/login",json=payload)
    assert response.status_code == 401 
    
def test_login_wrong_credential(client):
    payload = {
        "username" :"Invalid",
        "password" :"IDK232323232"
    }
    response = client.post("auth/login",json=payload)
    assert response.status_code == 401 

