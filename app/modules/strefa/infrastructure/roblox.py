"""Roblox helper: validate that a username/profile exists."""
from __future__ import annotations

import logging

import aiohttp

logger = logging.getLogger("bot_argon.roblox")

USER_AGENT = "StrefaArgonBot/0.3 (Discord; +https://github.com/KwanekDev/Bot-Argon)"


async def roblox_username_exists(nick: str) -> bool:
    url = f"https://www.roblox.com/users/profile?username={nick}"
    headers = {"User-Agent": USER_AGENT}
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    return False
                text = await resp.text()
        return f">profile?username={nick.lower()}" in text.lower() or "profile" in text.lower()
    except Exception:
        logger.exception("Roblox lookup failed")
        return False

