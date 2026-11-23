"""FastAPI application factory for Bot Argon."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.database import init_db
from app.core.ratelimit import limited, limiter
from app.core.settings import get_settings
from app.modules.authentication.presentation.routers import (
    admin_router,
    router as auth_router,
)
from app.modules.warns.presentation.routers import router as warns_router
from app.modules.content.presentation.routers import router as content_router
from app.modules.permissions.presentation.routers import router as permissions_router
from app.modules.webhooks.presentation.routers import router as webhooks_router

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


app = FastAPI(title=settings.app_title, version=settings.app_version, lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth_router)
app.include_router(warns_router)
app.include_router(admin_router)
app.include_router(content_router)
app.include_router(permissions_router)
app.include_router(webhooks_router)


@app.get("/health")
@limited(settings.rate_limit)
async def health(request: Request) -> dict:
    return {"status": "ok"}

