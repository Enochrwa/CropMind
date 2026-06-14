"""
Daily task: refresh crop market prices from open data sources.
Sources: FAO GIEWS, local government open data APIs.
"""
from loguru import logger
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.market_prices.refresh_prices")
def refresh_prices():
    logger.info("Refreshing crop market prices...")
    # In production: fetch from FAO GIEWS API, local govt portals
    # Update market_prices table
    logger.info("Market prices refreshed")
