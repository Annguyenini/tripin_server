import pytest
@pytest.fixture(scope="session")
def  get_jwt(client,user_credential):
    response = client.post("/auth/login",json=user_credential)
    assert response.get_json() is not None
    assert response.get_json()['tokens'] is not None
    return response.get_json()['tokens']
    
def test_login_with_token(client,get_jwt):
    headers ={
        "Authorization":f"Bearer {get_jwt['access_token']}"
    }
    response = client.post("/auth/login-via-token",headers=headers)
    assert response.status_code ==200
    

def test_login_with_invalid_token(client,invalid_jwt):
    
    headers ={
        "Authorization":f"Bearer {invalid_jwt['invalid_access_token']}"
    }
    response = client.post("/auth/login-via-token",headers=headers)
    assert response.status_code ==401
    
def test_login_with_expired_token(client,invalid_jwt):
    
    headers ={
        "Authorization":f"Bearer {invalid_jwt['expired_access_token']}"
    }
    response = client.post("/auth/login-via-token",headers=headers)
    assert response.status_code ==401
    
def test_request_new_access_invalid_token(client,invalid_jwt):
    headers ={
        "Authorization":f"Bearer {invalid_jwt['invalid_refresh_token']}"
    }
    response = client.post("/auth/request-access-token",headers=headers)
    assert response.status_code ==401
    
def test_request_new_access_expired_token(client,invalid_jwt):
    headers ={
        "Authorization":f"Bearer {invalid_jwt['expired_refresh_token']}"
    }
    response = client.post("/auth/request-access-token",headers=headers)
    assert response.status_code ==401
    
    
def test_request_new_access_token(get_jwt,client):
    headers ={
        "Authorization":f"Bearer {get_jwt['refresh_token']}"
    }
    response = client.post("/auth/request-access-token",headers=headers)
    assert response.status_code ==200
    