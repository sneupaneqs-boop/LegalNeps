import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from . import config
from .retrieval import get_index, index_ready
from .routes.chat import router as chat_router

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Build/load the search index in the background so the port opens at once
    # (hosts like Render kill services that don't bind quickly); requests that
    # arrive meanwhile simply wait for it inside get_index().
    warmup = asyncio.create_task(asyncio.to_thread(get_index))
    yield
    warmup.cancel()


app = FastAPI(title="Kanooni Sathi API", version="0.2.0", lifespan=lifespan)


class _GZipExceptStreams:
    """gzip buffers a streamed body until it ends, which would defeat
    /api/chat/stream; compress everything else."""

    def __init__(self, app):
        self.plain = app
        self.gzip = GZipMiddleware(app, minimum_size=1024)

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"].endswith("/stream"):
            return await self.plain(scope, receive, send)
        return await self.gzip(scope, receive, send)


app.add_middleware(_GZipExceptStreams)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_origin_regex=config.CORS_ORIGIN_REGEX or None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")


@app.get("/")
async def root():
    return {"msg": "Kanooni Sathi API is online"}


@app.get("/api/health")
async def health():
    return {"ok": True, "index_ready": index_ready()}
