"""FastAPI application for Bot Argon.

Run with: uvicorn api.main:app --reload
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from api.app.config import get_settings
from api.app.ratelimit import limited, limiter
from api.app.routers import admin, auth, warns
from database.connection import connect, init_schema

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    connection = await connect()
    try:
        await init_schema(connection)
    finally:
        await connection.close()
    yield


app = FastAPI(title="Bot Argon API", version="0.1.0", lifespan=lifespan)
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

app.include_router(auth.router)
app.include_router(warns.router)
app.include_router(admin.router)


@app.get("/health")
@limited(settings.rate_limit)
async def health(request: Request) -> dict:
    return {"status": "ok"}
