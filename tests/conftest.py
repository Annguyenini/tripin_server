import os

import pytest
from redis import Redis

from app import create_app


@pytest.fixture(scope="session")
def redis_client():
    host = os.getenv("REDIS_HOST")
    port = os.getenv("REDIS_PORT")
    yield Redis(host=host, port=port, decode_responses=True)


@pytest.fixture(scope="session")
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="session")
def user_credential():
    return {
        "username": "TestUser",
        "password": "Testpass11234@",
        "invalid_username": "Testting",
        "invalid_password": "Testting7749@",
    }


@pytest.fixture(scope="session")
def invalid_jwt():
    return {
        "invalid_access_token": os.getenv("INVALID_ACCESS_JWT"),
        "invalid_refresh_token": os.getenv("INVALID_REFRESH_JWT"),
        "expired_access_token": os.getenv("EXPIRED_ACCESS_JWT"),
        "expired_refresh_token": os.getenv("EXPIRED_REFRESH_JWT"),
    }


@pytest.fixture(scope="session")
def get_auth(client, user_credential):
    response = client.post("/auth/login", json=user_credential)
    print(response.get_json(), user_credential)

    assert response.get_json() is not None
    assert response.get_json()["tokens"] is not None
    return response.get_json()


@pytest.fixture(scope="session")
def user_data(client, user_credential, get_auth):
    username = user_credential["username"]
    password = user_credential["password"]
    res = client.get(
        "/user/get-user-data",
        headers={"Authorization": f"Bearer {get_auth['tokens']['access_token']}"},
    )
    return res.get_json()


@pytest.fixture(scope="session")
def get_header(get_auth):
    return {"Authorization": f"Bearer {get_auth['tokens']['access_token']}"}


@pytest.fixture(scope="session")
def get_test_trip_name():
    return os.getenv("TEST_TRIP_NAME") or None
