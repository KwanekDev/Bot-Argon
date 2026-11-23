"""Best-effort Roblox profile client (public profile page)."""
from __future__ import annotations

import html
import logging
import re

import aiohttp

logger = logging.getLogger("bot_argon.roblox")

ABOUT_ME_RE = re.compile(r'id="about-me-text"[^>]*>([^<]*)<', re.IGNORECASE)
USER_AGENT = "BotArgon/0.2 (Discord verification bot; +https://github.com/KwanekDev/Bot-Argon)"


class RobloxProfileClient:
    async def fetch_blurb(self, roblox_id: str) -> str | None:
        url = f"https://www.roblox.com/users/{roblox_id}/profile"
        headers = {"User-Agent": USER_AGENT, "Accept": "text/html"}
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status != 200:
                        logger.warning("Roblox profile returned status %s", resp.status)
                        return None
                    page = await resp.text()
        except Exception:
            logger.exception("Failed to fetch Roblox profile")
            return None

        match = ABOUT_ME_RE.search(page)
        if not match:
            return None
        text = html.unescape(match.group(1)).strip()
        return text or None

