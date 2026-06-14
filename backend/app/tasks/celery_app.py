from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "cropmind",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.outbreak_aggregator", "app.tasks.market_prices"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    beat_schedule={
        "aggregate-outbreaks-weekly": {
            "task": "app.tasks.outbreak_aggregator.aggregate_outbreaks",
            "schedule": 604800.0,  # every week
        },
        "refresh-market-prices-daily": {
            "task": "app.tasks.market_prices.refresh_prices",
            "schedule": 86400.0,  # every day
        },
    },
)
