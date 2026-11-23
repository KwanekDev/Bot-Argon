from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.authentication.presentation.routers import require_admin
from app.modules.webhooks.application.use_cases import WebhookUseCases
from app.modules.webhooks.presentation.dependencies import get_webhook_use_cases
from app.modules.webhooks.presentation.schemas import WebhookCreate, WebhookOut, WebhookUpdate

router = APIRouter(prefix="/api/v1/admin/webhooks", tags=["webhooks"])


@router.get("", response_model=list[WebhookOut])
async def list_webhooks(
    admin: dict = Depends(require_admin),
    use_cases: WebhookUseCases = Depends(get_webhook_use_cases),
) -> list[WebhookOut]:
    entities = await use_cases.list()
    return [WebhookOut(id=e.id, name=e.name, url=e.url, color=e.color, enabled=e.enabled) for e in entities]


@router.post("", response_model=WebhookOut, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    payload: WebhookCreate,
    admin: dict = Depends(require_admin),
    use_cases: WebhookUseCases = Depends(get_webhook_use_cases),
) -> WebhookOut:
    entity = await use_cases.create(payload.name, payload.url, payload.color)
    return WebhookOut(id=entity.id, name=entity.name, url=entity.url, color=entity.color, enabled=entity.enabled)


@router.patch("/{webhook_id}", response_model=WebhookOut)
async def patch_webhook(
    webhook_id: int,
    payload: WebhookUpdate,
    admin: dict = Depends(require_admin),
    use_cases: WebhookUseCases = Depends(get_webhook_use_cases),
) -> WebhookOut:
    entity = await use_cases.update(webhook_id, **payload.model_dump(exclude_unset=True))
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")
    return WebhookOut(id=entity.id, name=entity.name, url=entity.url, color=entity.color, enabled=entity.enabled)


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: int,
    admin: dict = Depends(require_admin),
    use_cases: WebhookUseCases = Depends(get_webhook_use_cases),
) -> None:
    deleted = await use_cases.delete(webhook_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")

