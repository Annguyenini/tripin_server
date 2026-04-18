import pytest
def test_login_with_token(client,get_auth):
    headers ={
        "Authorization":f"Bearer {get_auth['tokens']['access_token']}"
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
    
    
def test_request_new_access_token(get_auth,client):
    headers ={
        "Authorization":f"Bearer {get_auth['tokens']['refresh_token']}"
    }
    response = client.post("/auth/request-access-token",headers=headers)
    assert response.status_code ==200
    