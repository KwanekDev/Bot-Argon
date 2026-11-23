"""Webhook HTTP client using aiohttp."""
from __future__ import annotations

import logging
import re
from typing import Any

import aiohttp

logger = logging.getLogger("bot_argon.webhooks")

URL_RE = re.compile(r"^https://discord.com/api/webhooks/(?P<id>d+)/(?P<token>[A-Za-z0-9_-]+)$")


class WebhookSender:
    async def send_embed(
        self,
        url: str,
        payload: dict[str, Any],
        color_override: int | None = None,
    ) -> bool:
        match = URL_RE.match(url)
        if not match:
            logger.warning("Invalid webhook URL provided")
            return False

        color = payload.get("color") if payload.get("color") is not None else color_override
        embed: dict[str, Any] = {}
        if payload.get("title") is not None:
            embed["title"] = payload["title"]
        if payload.get("description") is not None:
            embed["description"] = payload["description"]
        if color is not None:
            embed["color"] = color
        if payload.get("thumbnail"):
            embed["thumbnail"] = {"url": payload["thumbnail"]}
        if payload.get("image"):
            embed["image"] = {"url": payload["image"]}
        if payload.get("footer"):
            embed["footer"] = {"text": payload["footer"].get("text", "")}
        if payload.get("fields"):
            embed["fields"] = payload["fields"]

        body = {"embeds": [embed]} if embed else {"content": payload.get("description") or ""}
        endpoint = f"https://discord.com/api/webhooks/{match.group('id')}/{match.group('token')}"

        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(endpoint, json=body) as resp:
                    if resp.status >= 400:
                        logger.warning("Webhook send failed with status %s", resp.status)
                        return False
                    return True
        except Exception:
            logger.exception("Webhook send failed")
            return False

