from dataclasses import dataclass


@dataclass(frozen=True)
class CommandPermissionEntity:
    command: str
    roles: list[str]
    permissions: list[str]

    @property
    def is_restricted(self) -> bool:
        return bool(self.roles) or bool(self.permissions)

