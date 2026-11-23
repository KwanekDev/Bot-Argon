from credentials import ADMIN_PASSWORD

from datetime import datetime, timedelta

from app.modules.verification.application.interfaces import RobloxProfileClient
from app.modules.verification.application.use_cases import VerificationUseCases
from app.modules.verification.domain.enums import VerificationStatus
from app.modules.verification.infrastructure.repositories import SqlAlchemyVerificationRepository
from app.modules.verification.domain.entities import PendingVerificationEntity


class FakeRobloxClient(RobloxProfileClient):
    def __init__(self, blurb: str | None) -> None:
        self.blurb = blurb

    async def fetch_blurb(self, roblox_id: str) -> str | None:
        return self.blurb


async def test_content_list_includes_seeds(client):
    token = await admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/admin/content", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert "verify.start" in body
    assert body["verify.start"]["title"]


async def test_content_patch_changes_fields(client):
    token = await admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.patch(
        "/api/v1/admin/content/verify.start",
        json={"color": 0, "description": "Nowy opis: **{code}**"},
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["color"] == 0
    assert body["description"] == "Nowy opis: **{code}**"


async def test_content_patch_invalid_payload(client):
    token = await admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.patch(
        "/api/v1/admin/content/verify.start",
        json={"color": -5},
        headers=headers,
    )
    assert response.status_code == 422


async def test_webhook_crud_and_color_change(client):
    token = await admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    created = await client.post(
        "/api/v1/admin/webhooks",
        json={"name": "logs", "url": "https://discord.com/api/webhooks/1/abc", "color": 255},
        headers=headers,
    )
    assert created.status_code == 201
    webhook_id = created.json()["id"]

    patched = await client.patch(
        f"/api/v1/admin/webhooks/{webhook_id}",
        json={"color": 65280},
        headers=headers,
    )
    assert patched.status_code == 200
    assert patched.json()["color"] == 65280

    listed = await client.get("/api/v1/admin/webhooks", headers=headers)
    assert any(w["id"] == webhook_id and w["color"] == 65280 for w in listed.json())

    deleted = await client.delete(f"/api/v1/admin/webhooks/{webhook_id}", headers=headers)
    assert deleted.status_code == 204


async def test_permissions_put_and_get(client):
    token = await admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.put(
        "/api/v1/admin/permissions/ban",
        json={"roles": ["Admin"], "permissions": []},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {"command": "ban", "roles": ["Admin"], "permissions": []}

    fetched = await client.get("/api/v1/admin/permissions/ban", headers=headers)
    assert fetched.json()["roles"] == ["Admin"]


async def test_verification_confirm_success(db_file):
    url, factory, _ = db_file
    async with factory() as session:
        repo = SqlAlchemyVerificationRepository(session)
        use_cases = VerificationUseCases(repo, FakeRobloxClient(""))
        code = await use_cases.start("user1", "123456")
        pending = await repo.get_pending("user1")
        use_cases = VerificationUseCases(repo, FakeRobloxClient(pending.code))
        status = await use_cases.confirm("user1")
        assert status == VerificationStatus.SUCCESS
        link = await repo.get_link_by_discord("user1")
        assert link is not None
        assert link.roblox_id == "123456"


async def test_verification_confirm_wrong_code(db_file):
    url, factory, _ = db_file
    async with factory() as session:
        repo = SqlAlchemyVerificationRepository(session)
        use_cases = VerificationUseCases(repo, FakeRobloxClient("WRONG"))
        await use_cases.start("user2", "123457")
        status = await use_cases.confirm("user2")
        assert status == VerificationStatus.FAIL_CODE


async def test_verification_confirm_missing_profile(db_file):
    url, factory, _ = db_file
    async with factory() as session:
        repo = SqlAlchemyVerificationRepository(session)
        use_cases = VerificationUseCases(repo, FakeRobloxClient(None))
        await use_cases.start("user3", "123458")
        status = await use_cases.confirm("user3")
        assert status == VerificationStatus.FAIL_NOTFOUND


async def test_verification_confirm_expired(db_file):
    url, factory, _ = db_file
    async with factory() as session:
        repo = SqlAlchemyVerificationRepository(session)
        await repo.save_pending(
            PendingVerificationEntity(
                discord_id="user4",
                code="ABC123",
                roblox_id="123459",
                expires_at=datetime.now() - timedelta(minutes=1),
            )
        )
        use_cases = VerificationUseCases(repo, FakeRobloxClient("ABC123"))
        status = await use_cases.confirm("user4")
        assert status == VerificationStatus.FAIL_EXPIRED


async def admin_token(client):
    response = await client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": ADMIN_PASSWORD},
    )
    return response.json()["access_token"]


if __name__ == "__main__":
    pass

