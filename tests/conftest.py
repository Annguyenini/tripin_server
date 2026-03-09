import pytest
import dotenv
import os
from app import create_app
dotenv.load_dotenv('.env.test')
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