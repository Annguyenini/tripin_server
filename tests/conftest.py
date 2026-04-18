import pytest
import dotenv
import os
from app import create_app

@pytest.fixture(scope="session")
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
        
        
@pytest.fixture(scope="session")
def user_credential():
    return {
        'username':os.getenv('TEST_USER'),
        'password':os.getenv('TEST_PASS'),
        'invalid_username':"test",
        'invalid_password':'Test'
    }
    
@pytest.fixture(scope="session")
def invalid_jwt():
    return {
        'invalid_access_token':os.getenv('INVALID_ACCESS_JWT'),
        'invalid_refresh_token':os.getenv('INVALID_REFRESH_JWT'),
        'expired_access_token':os.getenv('EXPIRED_ACCESS_JWT'),
        'expired_refresh_token':os.getenv('EXPIRED_REFRESH_JWT')
    }
@pytest.fixture(scope="session")
def get_auth(client,user_credential):
    response = client.post("/auth/login",json=user_credential)
    print(response.get_json())

    assert response.get_json() is not None
    assert response.get_json()['tokens'] is not None
    return response.get_json()
@pytest.fixture(scope="session")
def user_data(client,user_credential,get_auth):
    username = user_credential['username']
    password = user_credential['password']
    res = client.post('/user/get-user-data',headers ={'Authorization':f'Bearer {get_auth['tokens']['access_token']}'},json={'user_id':get_auth['user_data']['user_id']})
    return res.get_json()
@pytest.fixture(scope='session')
def get_header(get_auth):
    return {'Authorization':f'Bearer {get_auth['tokens']['access_token']}'}

@pytest.fixture(scope='session')
def get_test_trip_name():
    return os.getenv('TEST_TRIP_NAME') or None