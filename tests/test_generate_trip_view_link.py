def test_generate_trip_view_link(client, get_auth):
    """User should be able to generate a shareable trip view link with an expiration."""
    auth = get_auth

    headers = {
        "Authorization": f"Bearer {auth['tokens']['access_token']}"
    }

    payload = {
        "trip_id": 1,
        "expired_days": 7,
    }

    response = client.post(
        "/trip-view/generate-trip-view-link",
        json=payload,
        headers=headers,
    )
    print(response)

    data = response.get_json()
    print(data)

    assert response.status_code == 200
    assert data is not None, "Response body was empty/null"
    assert "url" in data, f"Unexpected response shape, got keys: {list(data.keys())}"
    # Optional: sanity check the link looks like a URL/token
    assert isinstance(data["url"], str)
    assert len(data["url"]) > 0
