def test_get_friend_list(client, get_auth):
    headers = {
        "Authorization": f"Bearer {get_auth['tokens']['access_token']}"
    }
    response = client.get("/friend/friends", headers=headers)
    data = response.get_json()
    friends = data["friends_list"]
    assert len(friends) == 1


def test_get_incoming_requests(client, get_auth):
    headers = {
        "Authorization": f"Bearer {get_auth['tokens']['access_token']}"
    }
    response = client.get("/friend/incoming-friend-requests", headers=headers)  # TODO: replace with your endpoint
    data = response.get_json()
    print(data)
    incoming = data["incoming_friend_requests"]  # TODO: replace with your response key
    assert len(incoming) == 2


def test_get_outgoing_requests(client, get_auth):
    headers = {
        "Authorization": f"Bearer {get_auth['tokens']['access_token']}"
    }
    response = client.get("/friend/outcoming-friend-requests", headers=headers)  # TODO: replace with your endpoint
    data = response.get_json()
    print(data)

    outgoing = data["outcoming_friend_requests"]  # TODO: replace with your response key
    assert len(outgoing) == 2


def test_accept_friend_request(client, get_auth):
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


def test_send_friend_request(client, get_auth):
    headers = {
        "Authorization": f"Bearer {get_auth['tokens']['access_token']}"
    }
    response = client.post(
        "/friend/request-friend",  # TODO: replace with your endpoint
        headers=headers,
        json={"target_user_id": 10},
    )
    assert response.status_code == 200  # TODO: confirm expected status code
    data = response.get_json()
    assert data["status"] in ("REQ_1", "REQ_2")  # TODO: replace with your response shape

def test_request_accept_flow_2to1(client,get_auth,get_auth2):
    headers2 = {
        "Authorization": f"Bearer {get_auth2['tokens']['access_token']}"
    }
    response2 = client.post(
        "/friend/request-friend",  # TODO: replace with your endpoint
        headers=headers2,
        json={"target_user_id": 1},
    )
    print(response2)
    assert response2.status_code == 200  # TODO: confirm expected status code
    data2 = response2.get_json()
    assert data2["status"] == "REQ_2"


    headers1 = {
        "Authorization": f"Bearer {get_auth['tokens']['access_token']}"
    }
    response1 = client.patch(
        "/friend/accept-friend-request",
        headers=headers1,
        json={"target_user_id": 2},
    )
    assert response1.status_code == 200
    data1 = response1.get_json()
    assert data1["status"] == "FRIEND"

def test_request_accept_flow_2to5(client,get_auth2,get_auth5):
    headers2 = {
        "Authorization": f"Bearer {get_auth2['tokens']['access_token']}"
    }
    response2 = client.post(
        "/friend/request-friend",  # TODO: replace with your endpoint
        headers=headers2,
        json={"target_user_id": 5},
    )
    print(response2)
    assert response2.status_code == 200  # TODO: confirm expected status code
    data2 = response2.get_json()
    assert data2["status"] == "REQ_1"


    headers1 = {
        "Authorization": f"Bearer {get_auth5['tokens']['access_token']}"
    }
    response1 = client.patch(
        "/friend/accept-friend-request",
        headers=headers1,
        json={"target_user_id": 2},
    )
    assert response1.status_code == 200
    data1 = response1.get_json()
    assert data1["status"] == "FRIEND"
def test_get_friend_list2(client, get_auth2):
    headers = {
        "Authorization": f"Bearer {get_auth2['tokens']['access_token']}"
    }
    response = client.get("/friend/friends", headers=headers)
    data = response.get_json()
    friends = data["friends_list"]
    assert len(friends) == 2
