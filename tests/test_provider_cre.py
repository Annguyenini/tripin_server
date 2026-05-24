import json
import os
import time
import uuid

import pytest


def _generate_pending_key(token: str) -> str:
    return f"new_user_pending_provider:token:{token}"


@pytest.fixture(scope="session")
def mock_token():
    return uuid.uuid4()


def _inject_new_user_into_cache(redis_client, mock_token):
    cache_key = _generate_pending_key(token=str(mock_token))
    fields = {
        "email": os.getenv("TEST_PROVIDER_EMAIL"),
        "provider_id": str(mock_token),
        "provider": os.getenv("TEST_PROVIDER"),
    }
    redis_client.setex(cache_key, 300, json.dumps(fields))


def test_mock_provider_signup(client, redis_client, mock_token):
    _inject_new_user_into_cache(redis_client, mock_token)
    field = {
        "pending_token": str(mock_token),
        "username": os.getenv("TEST_PROVIDER_USER"),
        "password": os.getenv("TEST_PROVIDER_PASS"),
        "display_name": os.getenv("TEST_PROVIDER_DISPLAYNAME"),
    }
    respond = client.post("auth/provider/complete-signup", json=field)
    assert respond.status_code == 200
