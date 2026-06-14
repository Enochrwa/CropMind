from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.models.diagnosis import Diagnosis

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/")
async def get_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, le=100),
    offset: int = 0,
):
    result = await db.execute(
        select(Diagnosis)
        .where(Diagnosis.user_id == current_user.id)
        .order_by(Diagnosis.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    diagnoses = result.scalars().all()
    return [
        {
            "id": str(d.id),
            "disease": d.disease_display_name,
            "crop": d.crop_type,
            "severity": d.severity,
            "confidence": d.confidence,
            "cost_rwf": d.cost_rwf,
            "created_at": d.created_at.isoformat(),
        }
        for d in diagnoses
    ]
