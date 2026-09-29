import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from . import config
from .retrieval import get_index, index_ready
from .routes.chat import router as chat_router
from .routes.documents import router as documents_router
from .routes.tools import router as tools_router

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# S14: no route needs a body bigger than this (the one binary upload,
# matter files, already enforces its own 20MB cap while streaming - see
# routes/chat.py:upload_matter_file); this is the outer backstop so an
# oversized body on ANY route (including ones that don't expect binary
# data at all) is rejected off a header, before the framework starts
# buffering/parsing it.
MAX_REQUEST_BODY_BYTES = 25 * 1024 * 1024


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


_PRIVATE_PATHS = ("/api/matters", "/api/research", "/api/drafting/drafts", "/api/company-profile",
                  "/api/llm-usage", "/api/documents")


@app.middleware("http")
async def _security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    if request.url.path.startswith(_PRIVATE_PATHS):
        response.headers.setdefault("Cache-Control", "no-store")  # user data: never cache in shared proxies
    return response


@app.middleware("http")
async def _reject_oversized_bodies(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            if int(content_length) > MAX_REQUEST_BODY_BYTES:
                return JSONResponse({"detail": "request body too large"}, status_code=413)
        except ValueError:
            pass  # malformed header: let the framework itself reject it
    return await call_next(request)


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
app.include_router(documents_router, prefix="/api")
app.include_router(tools_router, prefix="/api")


@app.get("/")
async def root():
    return {"msg": "Kanooni Sathi API is online"}


@app.get("/api/health")
async def health():
    return {"ok": True, "index_ready": index_ready()}
