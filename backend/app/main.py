from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from loguru import logger

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1 import api_router
from app.ml.inference import load_model
from app.services.whisper_service import load_whisper
from app.services.translation_service import load_translation_models


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info(f"🌱 CropMind {settings.APP_VERSION} starting up...")

    # Load ML models at startup (async-friendly background loading)
    logger.info("Loading ONNX inference model...")
    load_model()

    logger.info("Loading Whisper transcription model...")
    load_whisper()

    if settings.APP_ENV == "production":
        logger.info("Loading translation models...")
        load_translation_models()

    logger.info("✅ CropMind ready to serve farmers worldwide!")
    yield
    logger.info("CropMind shutting down...")


app = FastAPI(
    title="CropMind API",
    description="AI-powered crop disease diagnosis for smallholder farmers worldwide.",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION, "service": "CropMind"}
