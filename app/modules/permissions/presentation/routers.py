from fastapi import APIRouter, Depends

from app.modules.authentication.presentation.routers import require_admin
from app.modules.permissions.application.use_cases import PermissionUseCases
from app.modules.permissions.presentation.dependencies import get_permission_use_cases
from app.modules.permissions.presentation.schemas import PermissionRule, PermissionRuleUpdate

router = APIRouter(prefix="/api/v1/admin/permissions", tags=["permissions"])


@router.get("", response_model=list[PermissionRule])
async def list_permissions(
    admin: dict = Depends(require_admin),
    use_cases: PermissionUseCases = Depends(get_permission_use_cases),
) -> list[PermissionRule]:
    entities = await use_cases.list()
    return [PermissionRule(command=e.command, roles=e.roles, permissions=e.permissions) for e in entities]


@router.get("/{command}", response_model=PermissionRule)
async def get_permission(
    command: str,
    admin: dict = Depends(require_admin),
    use_cases: PermissionUseCases = Depends(get_permission_use_cases),
) -> PermissionRule:
    entity = await use_cases.get(command)
    if entity is None:
        return PermissionRule(command=command)
    return PermissionRule(command=entity.command, roles=entity.roles, permissions=entity.permissions)


@router.put("/{command}", response_model=PermissionRule)
async def put_permission(
    command: str,
    payload: PermissionRuleUpdate,
    admin: dict = Depends(require_admin),
    use_cases: PermissionUseCases = Depends(get_permission_use_cases),
) -> PermissionRule:
    entity = await use_cases.set(command, payload.roles, payload.permissions)
    return PermissionRule(command=entity.command, roles=entity.roles, permissions=entity.permissions)

