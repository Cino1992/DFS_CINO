def test_register_user(client, test_user):
    response = client.post("/api/v1/users", json=test_user)
    assert response.status_code == 200
    assert response.json()["email"] == test_user["email"]
    assert response.json()["username"] == test_user["username"]
    assert "id" in response.json()


def test_login(client, test_user):
    # Register user
    client.post("/api/v1/users", json=test_user)

    # Login
    response = client.post(
        "/api/v1/token",
        data={"username": test_user["username"], "password": test_user["password"]}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()


def test_get_current_user(client, auth_headers, test_user):
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == test_user["email"]
    assert response.json()["username"] == test_user["username"]