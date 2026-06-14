from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional
from app.db.session import get_db

router = APIRouter(prefix="/outbreaks", tags=["outbreaks"])


@router.get("/heatmap")
async def get_heatmap(
    country: Optional[str] = Query(None),
    disease: Optional[str] = Query(None),
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns disease outbreak data for heatmap visualization.
    Used by: government ministries, NGOs, agro-input companies.
    This endpoint requires a B2B API key (billed separately).
    """
    query = text("""
        SELECT
            confirmed_disease AS disease,
            crop_type,
            country,
            region,
            COUNT(*) AS case_count,
            AVG(CASE severity
                WHEN 'critical' THEN 4
                WHEN 'high' THEN 3
                WHEN 'medium' THEN 2
                ELSE 1 END) AS severity_avg,
            ST_AsGeoJSON(ST_Centroid(ST_Collect(location::geometry)))::json AS centroid,
            DATE_TRUNC('week', created_at) AS week_of
        FROM diagnoses
        WHERE
            created_at >= NOW() - INTERVAL ':days days'
            AND location IS NOT NULL
            AND (:country IS NULL OR country = :country)
            AND (:disease IS NULL OR confirmed_disease = :disease)
        GROUP BY confirmed_disease, crop_type, country, region, DATE_TRUNC('week', created_at)
        ORDER BY case_count DESC
        LIMIT 500
    """)
    result = await db.execute(query, {"days": days, "country": country, "disease": disease})
    rows = result.fetchall()
    return {
        "features": [
            {
                "disease": r.disease,
                "crop": r.crop_type,
                "country": r.country,
                "region": r.region,
                "cases": r.case_count,
                "severity_avg": round(float(r.severity_avg), 2),
                "centroid": r.centroid,
                "week_of": str(r.week_of),
            }
            for r in rows
        ],
        "total": len(rows),
        "period_days": days,
    }
