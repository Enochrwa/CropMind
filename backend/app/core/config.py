from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "CropMind"
    APP_ENV: str = "development"
    APP_VERSION: str = "1.0.0"
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://cropmind:password@localhost:5432/cropmind"
    SYNC_DATABASE_URL: str = "postgresql://cropmind:password@localhost:5432/cropmind"

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral:7b-instruct-q4_K_M"

    # Whisper
    WHISPER_MODEL: str = "small"
    WHISPER_DEVICE: str = "cpu"

    # ML
    ONNX_MODEL_PATH: str = "app/ml/models/cropmind_v1.onnx"
    TFLITE_MODEL_PATH: str = "app/ml/models/cropmind_v1.tflite"
    CONFIDENCE_THRESHOLD: float = 0.65

    # Storage
    S3_BUCKET: str = "cropmind-uploads"
    S3_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    # Balance
    DIAGNOSIS_COST_RWF: int = 600
    VOICE_COST_PER_MINUTE_RWF: int = 50
    MIN_TOPUP_RWF: int = 500
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Translation
    TRANSLATION_MODEL_DIR: str = "app/ml/translation_models"

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8081"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
