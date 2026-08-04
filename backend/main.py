from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.providers.cloudflare import generate

from app.utils.config import APP_ENV

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("VibeOS backend starting...")
    yield
    print("VibeOS backend shutting down...")

app = FastAPI(
    title="VibeOS",
    description="AI workspace that builds software through conversation",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": "VibeOS",
        "env": APP_ENV
    }



