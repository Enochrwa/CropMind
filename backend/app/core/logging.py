import sys
from loguru import logger
from app.core.config import settings


def setup_logging() -> None:
    logger.remove()
    level = "DEBUG" if settings.APP_ENV == "development" else "INFO"
    logger.add(
        sys.stdout,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan> - {message}",
        colorize=True,
    )
    logger.add(
        "logs/cropmind.log",
        rotation="10 MB",
        retention="30 days",
        level="INFO",
        compression="gz",
    )
