from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config
from .routes.chat import router as chat_router

app = FastAPI(title="Kanooni Sathi API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")


@app.get("/")
async def root():
    return {"msg": "Kanooni Sathi API is online"}
