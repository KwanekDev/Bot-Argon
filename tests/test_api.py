async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_login_success(client):
    response = await client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["expires_in"] > 0


async def test_login_bad_password(client):
    response = await client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "wrong"},
    )
    assert response.status_code == 401


async def test_me_requires_auth(client):
    assert (await client.get("/api/v1/auth/me")).status_code == 401


async def test_me_with_token(client):
    token = (
        await client.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "admin123"},
        )
    ).json()["access_token"]
    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"username": "admin", "role": "admin"}


async def test_warns_requires_auth(client):
    assert (await client.get("/api/v1/warns")).status_code == 401


async def test_warns_with_token(client):
    token = (
        await client.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "admin123"},
        )
    ).json()["access_token"]
    response = await client.get(
        "/api/v1/warns", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["user_id"] == 111
    assert body[0]["reason"] == "test warn"


async def test_admin_health_requires_key(client):
    assert (await client.get("/api/v1/admin/health")).status_code == 403


async def test_admin_health_with_invalid_key(client):
    response = await client.get(
        "/api/v1/admin/health", headers={"X-API-Key": "nope"}
    )
    assert response.status_code == 403


async def test_admin_health_with_valid_key(client, api_key):
    response = await client.get(
        "/api/v1/admin/health", headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


async def test_api_key_lifecycle(client):
    admin_token = (
        await client.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "admin123"},
        )
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    created = await client.post("/api/v1/admin/api-keys", json={"name": "svc"}, headers=headers)
    assert created.status_code == 201
    body = created.json()
    assert body["key"]
    key_id = body["id"]

    listed = await client.get("/api/v1/admin/api-keys", headers=headers)
    assert listed.status_code == 200
    assert any(k["id"] == key_id for k in listed.json())

    rotated = await client.post(f"/api/v1/admin/api-keys/{key_id}/rotate", headers=headers)
    assert rotated.status_code == 200
    new_key = rotated.json()["key"]
    assert new_key != body["key"]

    deleted = await client.delete(f"/api/v1/admin/api-keys/{key_id}", headers=headers)
    assert deleted.status_code == 204

    listed_after = await client.get("/api/v1/admin/api-keys", headers=headers)
    assert all(k["id"] != key_id for k in listed_after.json())

