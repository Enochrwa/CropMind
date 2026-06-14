"""
Regional supplier lookup using PostGIS spatial queries.
Returns suppliers within radius that carry relevant products.
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from loguru import logger
from app.schemas.diagnosis import SupplierResult


async def find_nearby_suppliers(
    disease_key: str,
    lat: float,
    lng: float,
    db: AsyncSession,
    radius_km: int = 50,
    limit: int = 5,
) -> List[SupplierResult]:
    try:
        query = text("""
            SELECT
                id::text,
                name,
                phone,
                whatsapp,
                address,
                is_verified,
                rating,
                ROUND(
                    ST_Distance(
                        location::geography,
                        ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography
                    ) / 1000.0, 1
                ) AS distance_km
            FROM suppliers
            WHERE
                is_active = TRUE
                AND ST_DWithin(
                    location::geography,
                    ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography,
                    :radius_m
                )
                AND (
                    products ILIKE :disease_pattern
                    OR products ILIKE '%general%'
                )
            ORDER BY distance_km ASC
            LIMIT :limit
        """)

        result = await db.execute(
            query,
            {
                "lat": lat,
                "lng": lng,
                "radius_m": radius_km * 1000,
                "disease_pattern": f"%{disease_key}%",
                "limit": limit,
            },
        )
        rows = result.fetchall()

        return [
            SupplierResult(
                id=str(row.id),
                name=row.name,
                phone=row.phone,
                whatsapp=row.whatsapp,
                distance_km=float(row.distance_km),
                address=row.address,
                is_verified=row.is_verified,
                rating=float(row.rating),
            )
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Supplier lookup error: {e}")
        return []
