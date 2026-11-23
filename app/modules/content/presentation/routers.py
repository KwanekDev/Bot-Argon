from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.authentication.presentation.routers import require_admin
from app.modules.content.application.use_cases import ContentUseCases
from app.modules.content.presentation.dependencies import get_content_use_cases
from app.modules.content.presentation.schemas import EmbedTemplate, EmbedTemplateUpdate

router = APIRouter(prefix="/api/v1/admin/content", tags=["content"])


@router.get("", response_model=dict[str, EmbedTemplate])
async def list_templates(
    admin: dict = Depends(require_admin),
    use_cases: ContentUseCases = Depends(get_content_use_cases),
) -> dict[str, EmbedTemplate]:
    templates = await use_cases.list_templates()
    return {t.key: EmbedTemplate(**t.payload) for t in templates}


@router.get("/{key}", response_model=EmbedTemplate)
async def get_template(
    key: str,
    admin: dict = Depends(require_admin),
    use_cases: ContentUseCases = Depends(get_content_use_cases),
) -> EmbedTemplate:
    template = await use_cases.get_template(key)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return EmbedTemplate(**template.payload)


@router.patch("/{key}", response_model=EmbedTemplate)
async def patch_template(
    key: str,
    update: EmbedTemplateUpdate,
    admin: dict = Depends(require_admin),
    use_cases: ContentUseCases = Depends(get_content_use_cases),
) -> EmbedTemplate:
    existing = await use_cases.get_template(key)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    merged = update.merged_payload(existing.payload)
    saved = await use_cases.update_template(key, merged)
    return EmbedTemplate(**saved.payload)

