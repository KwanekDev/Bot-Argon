"""Render event/command message sequences from stefa_source JSON.

Each event payload has a "messages" list. Supported kinds:
- content: message content (plain text, may contain placeholders)
- setcolor: embed color (hex string)
- footer: {text, icon}
- setdescription: embed description (markdown)
- setthumbnail_raw: formula returning avatar URL (handled by caller helpers)
"""
from __future__ import annotations

import re
from typing import Any

PLACEHOLDER_RE = re.compile(r"{([A-Za-z_][A-Za-z0-9_]*)}")


def render(value: Any, variables: dict[str, Any]) -> Any:
    if isinstance(value, str):
        return PLACEHOLDER_RE.sub(lambda m: str(variables.get(m.group(1), m.group(0))), value)
    if isinstance(value, dict):
        return {k: render(v, variables) for k, v in value.items()}
    if isinstance(value, list):
        return [render(v, variables) for v in value]
    return value


def hex_to_int(value: str) -> int:
    return int(value.lstrip("#"), 16) if value else 0


def build_event_output(payload: dict[str, Any], variables: dict[str, Any]) -> dict[str, Any]:
    """Return {content, embed_kwargs, thumbnail_formula}."""
    content = ""
    embed: dict[str, Any] = {}
    thumbnail_formula = None
    for msg in payload.get("messages", []):
        kind = msg.get("kind")
        if kind == "content":
            content += msg.get("value", "")
        elif kind == "setcolor":
            embed["color"] = hex_to_int(str(render(msg.get("value", ""), variables)))
        elif kind == "footer":
            footer = render(msg, variables)
            embed["footer"] = {"text": footer.get("text", ""), "icon_url": footer.get("icon")}
        elif kind == "setdescription":
            embed["description"] = render(msg.get("value", ""), variables)
        elif kind == "setthumbnail_raw":
            thumbnail_formula = msg.get("value")
    return {"content": render(content, variables), "embed": embed, "thumbnail_formula": thumbnail_formula}

