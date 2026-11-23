from typing import Any

from pydantic import BaseModel, Field


class EmbedField(BaseModel):
    name: str
    value: str
    inline: bool = False


class EmbedButton(BaseModel):
    label: str
    style: int = Field(2, ge=1, le=5)
    url: str | None = None
    custom_id: str | None = None


class EmbedTemplate(BaseModel):
    title: str | None = None
    description: str | None = None
    color: int | None = Field(None, ge=0, le=16777215)
    fields: list[EmbedField] = Field(default_factory=list)
    thumbnail: str | None = None
    image: str | None = None
    footer: dict[str, str] | None = None
    buttons: list[EmbedButton] = Field(default_factory=list)


class EmbedTemplateUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    color: int | None = Field(None, ge=0, le=16777215)
    fields: list[EmbedField] | None = None
    thumbnail: str | None = None
    image: str | None = None
    footer: dict[str, str] | None = None
    buttons: list[EmbedButton] | None = None

    def merged_payload(self, current: dict[str, Any]) -> dict[str, Any]:
        data = dict(current)
        updates = self.model_dump(exclude_unset=True)
        for field in ("title", "description", "color", "thumbnail", "image", "footer"):
            if field in updates:
                data[field] = updates[field]
        if "fields" in updates:
            data["fields"] = [f.model_dump() for f in updates["fields"]]
        if "buttons" in updates:
            data["buttons"] = [b.model_dump() for b in updates["buttons"]]
        return data

