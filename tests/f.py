def get_friend_list(client, get_auth):
    headers = {
        "Authorization": f"Bearer {get_auth['tokens']['access_token']}"
    }
    response = client.get("/friend/friends", headers=headers)
    data = response.get_json()
    friends = data["friends_list"]
    assert len(friends) == 2


def get_incoming_requests(client, get_auth):
    headers = {
        "Authorization": f"Bearer {get_auth['tokens']['access_token']}"
    }
    response = client.get("/friend/incoming-friend-requests", headers=headers)  # TODO: replace with your endpoint
    data = response.get_json()
    incoming = data["incoming_list"]  # TODO: replace with your response key
    assert len(incoming) == 2


def get_outgoing_requests(client, get_auth):
    headers = {
        "Authorization": f"Bearer {get_auth['tokens']['access_token']}"
    }
    response = client.get("/friend/outcoming-friend-requests", headers=headers)  # TODO: replace with your endpoint
    data = response.get_json()
    outgoing = data["outgoing_list"]  # TODO: replace with your response key
    assert len(outgoing) == 2


def accept_friend_request(client, get_auth):
    headers = {
        "Authorization": f"Bearer {get_auth['tokens']['access_token']}"
    }
    response = client.patch(  # TODO: confirm PATCH vs POST for your route
        "/friend/accept-friend-request",  # TODO: replace with your endpoint
        headers=headers,
        json={"target_user_id": 4},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "FRIEND"  # TODO: replace with your response shape


def send_friend_request(client, get_auth):
    headers = {
        "Authorization": f"Bearer {get_auth['tokens']['access_token']}"
    }
    response = client.post(
        "/friend/request",  # TODO: replace with your endpoint
        headers=headers,
        json={"target_user_id": 10},
    )
    assert response.status_code == 201  # TODO: confirm expected status code
    data = response.get_json()
    assert data["status"] in ("REQ_1", "REQ_2")  # TODO: replace with your response shape
