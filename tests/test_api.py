
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
    assert response.json() == []


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
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}
