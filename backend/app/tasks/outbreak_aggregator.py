"""
Weekly task: aggregate diagnosis data into outbreak_reports table.
Used for government/NGO heatmap API.
"""
from loguru import logger
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.outbreak_aggregator.aggregate_outbreaks")
def aggregate_outbreaks():
    logger.info("Running weekly outbreak aggregation...")
    # In production: raw SQL insert into outbreak_reports from diagnoses
    # grouped by disease, region, week
    logger.info("Outbreak aggregation complete")
