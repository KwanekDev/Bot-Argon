"""Shared rate-limit helpers."""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.settings import get_settings

settings = get_settings()
limiter = Limiter(key_func=get_remote_address)


def limited(rate: str):
    """Apply a rate limit unless throttling is disabled (e.g. in tests)."""

    def decorator(func):
        if not settings.slowapi_enabled:
            return func
        return limiter.limit(rate)(func)

    return decorator

