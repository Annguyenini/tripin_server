import pytest


# Relies on seed data:
#   - user 3 is FRIEND with user 1        (mock_relations: (3, "FRIEND"))
#   - user 4 is a stranger to user 1       (mock_relations: (4, ("PENDING", 4)) -> pending, not friend)
#   - user 1's trips seeded via seed_trips.py:
#       private: "Solo Japan Trip", "Weekend in Big Sur"
#       friend:  "College Friends Reunion", "Camping w/ Roommates"
#       public:  "Backpacking SE Asia", "Currently in Iceland"


def test_friend_sees_friend_and_public_trips(client,gen_auth):

    auth = gen_auth(3)
    """User 3 (friend of user 1) should see friend + public trips of user 1 -> 4 total."""
    headers3 = {
        "Authorization": f"Bearer {auth['tokens']['access_token']}"
    }
    response = client.get(
        "/users/trips/1",  # TODO: replace with your actual "get user's trips" endpoint
        headers=headers3,
    )
    print(response)
    assert response.status_code == 200  # TODO: confirm expected status code

    data = response.get_json()
    print(data)
    trips = data["all_trip_data"]  # TODO: confirm response key holding the trip list

    assert len(trips) == 4

    expected = {
        ("College Friends Reunion", "friend"),
        ("Camping w/ Roommates", "friend"),
        ("Backpacking SE Asia", "public"),
        ("Currently in Iceland", "public"),
    }
    actual = {(t["trip_name"], t["privacy"]) for t in trips}
    assert actual == expected

    # sanity: no private trips should ever leak to a friend
    assert all(t["privacy"] != "private" for t in trips)


def test_stranger_sees_only_public_trips(client, gen_auth):
    """User 5 (stranger to user 1) should only see public trips of user 1 -> 2 total."""
    auth = gen_auth(5)

    headers4 = {
        "Authorization": f"Bearer {auth['tokens']['access_token']}"
    }
    response = client.get(
        "/users/trips/1",  # TODO: replace with your actual "get user's trips" endpoint
        headers=headers4,
    )
    print(response)
    assert response.status_code == 200  # TODO: confirm expected status code

    data = response.get_json()
    print(data)
    trips = data["all_trip_data"]  # TODO: confirm response key holding the trip list

    assert len(trips) == 2

    expected = {
        ("Backpacking SE Asia", "public"),
        ("Currently in Iceland", "public"),
    }
    actual = {(t["trip_name"], t["privacy"]) for t in trips}  # TODO: confirm field names
    assert actual == expected

    # sanity: strangers should never see private or friend-only trips
    assert all(t["privacy"] == "public" for t in trips)
